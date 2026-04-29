import argparse
import base64
import contextlib
import json
import logging
import multiprocessing
import os
import re
import subprocess
import sys
from functools import partial
from pathlib import Path

import backoff
import openai
from google import genai
from google.api_core.exceptions import ResourceExhausted
from google.genai.errors import ClientError as GenaiClientError
from google.genai.errors import ServerError as GenaiServerError
from openai import OpenAI
from PIL import Image

logger = logging.getLogger(__name__)

# API key resolution: --api_key_txt flag > credentials/{gemini,openai}_api.txt (auto-inferred from model) > env vars

GEOMETRY_N_VIEWS = 2


def get_n_views(task_name: str) -> int | None:
    """Return number of views to use for a task. None means use single render."""
    if task_name.startswith("geometry"):
        return GEOMETRY_N_VIEWS
    return None

# Global semaphore for limiting concurrent renders (set via init_worker for multiprocessing)
_render_sem = None

def init_worker(sem):
    global _render_sem
    _render_sem = sem

def render_lock():
    """Context manager for render semaphore. No-op if semaphore not set."""
    if _render_sem is None:
        return contextlib.nullcontext()
    return _render_sem


def extract_code(response: str) -> str | None:
    pattern = r"```python\s*(.*?)\s*```"
    matches = re.findall(pattern, response, re.DOTALL)
    if not matches:
        return None
    return matches[-1]


def get_render_path(render_dir: Path, n_views: int | None = None) -> Path | None:
    """Get render from a directory.

    If n_views is None, returns render.png if it exists, else first numbered render.
    If n_views is specified, concatenates exactly that many numbered renders.
    """
    render_path = render_dir / "render.png"
    numbered = sorted(render_dir.glob("render[0-9]*.png"))

    if n_views is None:
        if render_path.exists():
            return render_path
        return numbered[0] if numbered else None

    if len(numbered) < n_views:
        raise ValueError(f"Expected {n_views} renders but found {len(numbered)} in {render_dir}")
    views = numbered[:n_views]
    if len(views) == 1:
        return views[0]
    return concat_images(views, render_path)


def concat_images(paths: list[Path], output_path: Path) -> Path:
    """Concatenate images horizontally. Returns first path if only one."""
    if len(paths) == 1:
        return paths[0]
    images = [Image.open(p) for p in paths]
    total_width = sum(img.width for img in images)
    max_height = max(img.height for img in images)
    merged = Image.new("RGB", (total_width, max_height))
    x_offset = 0
    for img in images:
        merged.paste(img, (x_offset, 0))
        x_offset += img.width
    merged.save(output_path)
    return output_path


# LLM backends


def log_gemini_tokens(response):
    usage = response.usage_metadata
    logger.debug(f"[PROMPT_TOKENS]: {usage.prompt_token_count}")
    logger.debug(f"[COMPLETION_TOKENS]: {usage.candidates_token_count}")
    logger.debug(f"[TOTAL_TOKENS]: {usage.total_token_count}")
    if hasattr(usage, "cached_content_token_count") and usage.cached_content_token_count:
        logger.debug(f"[CACHED_TOKENS]: {usage.cached_content_token_count}")
    if hasattr(usage, "thoughts_token_count") and usage.thoughts_token_count:
        logger.debug(f"[THINKING_TOKENS]: {usage.thoughts_token_count}")


def truncate(text: str, n: int = 100) -> str:
    text = text.replace("\n", "\\n")
    return text[:n] + "..." if len(text) > n else text

def get_git_hash():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    except Exception:
        return None

def build_summary(args, tasks: list, crashes: list) -> dict:
    total_rounds = len(tasks) * args.rounds
    crash_rate = len(crashes) / total_rounds * 100 if total_rounds else 0
    return {
        "config": {
            "command": " ".join(sys.argv),
            "git_hash": get_git_hash(),
            "args": {k: str(v) for k, v in vars(args).items()},
        },
        "tasks": tasks,
        "num_tasks": len(tasks),
        "total_rounds": total_rounds,
        "crashes": crashes,
        "crash_rate": round(crash_rate, 1),
    }


def log_backoff(details):
    exc = details.get('exception')
    exc_info = f" | {type(exc).__name__}: {exc}" if exc else ""
    logger.warning(f"[RATELIMIT] attempt {details['tries']}, retrying in {details['wait']:.1f}s{exc_info}")

def log_giveup(details):
    exc = details.get('exception')
    exc_info = f" | {type(exc).__name__}: {exc}" if exc else ""
    logger.warning(f"[RATELIMIT] giving up after {details['tries']} attempts, {details['elapsed']:.1f}s elapsed{exc_info}")


def _content_for_openai(parts: list) -> list:
    """Convert parts list to OpenAI content format."""
    content = []
    for part in parts:
        if isinstance(part, str):
            content.append({"type": "text", "text": part})
        elif isinstance(part, Path):
            b64 = base64.b64encode(part.read_bytes()).decode("utf-8")
            content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}", "detail": "high"}})
    return content


def _is_retryable_gemini_error(e):
    if isinstance(e, ResourceExhausted):
        return True
    if isinstance(e, GenaiServerError):
        return True
    if isinstance(e, GenaiClientError):
        return getattr(e, 'code', None) == 429
    return False

@backoff.on_exception(backoff.expo, (ResourceExhausted, GenaiClientError, GenaiServerError), giveup=lambda e: not _is_retryable_gemini_error(e), on_backoff=log_backoff, on_giveup=log_giveup, max_value=300, max_time=600)
def call_gemini(client, parts: list) -> str:
    """Send message to Gemini. parts is list of str or Path."""
    content = [Image.open(p) if isinstance(p, Path) else p for p in parts]
    response = client["chat"].send_message(content)
    log_gemini_tokens(response)
    return response.text


@backoff.on_exception(backoff.expo, openai.RateLimitError, max_time=300, on_backoff=log_backoff, on_giveup=log_giveup)
def call_openai(client, model: str, parts: list) -> str:
    """Send message to OpenAI. parts is list of str or Path."""
    content = _content_for_openai(parts)
    if not client["messages"] or client["messages"][-1].get("content") != content:
        client["messages"].append({"role": "user", "content": content})

    kwargs = dict(
        model=model,
        messages=client["messages"],
    )

    kwargs["max_completion_tokens"] = 10000

    if model.startswith("o"):
        kwargs["reasoning"] = {"effort": "low"}

    try:
        response = client["client"].chat.completions.create(**kwargs)
    except openai.APIStatusError as e:
        raise RuntimeError(f"OpenAI API error: {e.status_code} {e.message}") from None
    usage = response.usage
    logger.debug(f"[PROMPT_TOKENS]: {usage.prompt_tokens}")
    logger.debug(f"[COMPLETION_TOKENS]: {usage.completion_tokens}")
    logger.debug(f"[TOTAL_TOKENS]: {usage.total_tokens}")
    response_text = response.choices[0].message.content
    client["messages"].append({"role": "assistant", "content": response_text})
    return response_text


# Import validation

BLOCKED_MODULES = {"sys", "os", "subprocess", "shutil", "requests", "urllib", "socket", "pickle", "ctypes"}


def check_imports(new_code: str) -> str | None:
    """Check if new code imports any blocked modules."""
    modules = re.findall(r'^\s*(?:import|from)\s+(\w+)', new_code, re.MULTILINE)
    blocked = set(modules) & BLOCKED_MODULES
    return f"Blocked imports: {', '.join(blocked)}" if blocked else None


# Render backends


def get_error(result: subprocess.CompletedProcess, default: str) -> str:
    if "Traceback" in (result.stdout or ""):
        error = result.stdout
    elif "Traceback" in (result.stderr or ""):
        error = result.stderr
    else:
        error = result.stderr or result.stdout or default
    return ("..." + error[-2000:]) if len(error) > 2000 else error


def render_pf(
    code_path: Path, render_dir: Path, blendfile: Path, n_views: int | None = None
) -> tuple[Path | str, list[str]]:
    """Returns (render Path on success or error message string, command list)."""
    render_script = Path(__file__).parent / "pipeline_render_script.py"
    cmd = [
        sys.executable,
        str(render_script),
        str(code_path),
        str(render_dir),
        "--base_blendfile_path",
        str(blendfile),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    (render_dir / "render_stdout.log").write_text(result.stdout or "")
    (render_dir / "render_stderr.log").write_text(result.stderr or "")

    try:
        render_path = get_render_path(render_dir, n_views)
    except ValueError as e:
        return get_error(result, str(e)), cmd
    if render_path is None:
        return get_error(result, f"no output file (exit code {result.returncode})"), cmd
    return render_path, cmd


def render_bgym(
    code_path: Path,
    render_dir: Path,
    blendfile: Path,
    blender_path: Path,
    render_script: Path,
    n_views: int | None = None,
) -> tuple[Path | str, list[str]]:
    """Returns (render Path on success or error message string, command list)."""
    cmd = [
        str(blender_path),
        "--background",
        str(blendfile),
        "--python",
        str(render_script),
        "--",
        str(code_path),
        str(render_dir),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    (render_dir / "render_stdout.log").write_text(result.stdout or "")
    (render_dir / "render_stderr.log").write_text(result.stderr or "")

    try:
        render_path = get_render_path(render_dir, n_views)
    except ValueError as e:
        return get_error(result, str(e)), cmd
    if render_path is None:
        return get_error(result, f"no output file (exit code {result.returncode})"), cmd
    return render_path, cmd


# Main round logic


def run_round(
    args,
    round_idx: int,
    client,
    current_code: str,
    last_result: Path | str,
    chat_data: dict,
    task_folder: Path,
    output_folder: Path,
) -> tuple[str, Path | str]:
    task = task_folder.name
    n_views = get_n_views(task)
    def log(msg):
        return logger.info(f"[{task}][r{round_idx}]{msg}")
    def logwarn(msg):
        return logger.warning(f"[{task}][r{round_idx}]{msg}")

    render_dir = output_folder / f"round_{round_idx:02d}"
    render_dir.mkdir(parents=True, exist_ok=True)
    code_path = render_dir / "code.py"
    blendfile = task_folder / "blender_file.blend"
    goal_render_dir = task_folder / "renders" / "goal"
    goal_render = get_render_path(goal_render_dir, n_views)
    assert goal_render is not None, f"Goal render not found in {goal_render_dir}"

    prompt_lines = [l for l in args.prompt_file.read_text().splitlines() if not l.startswith("#")]
    main_prompt = "\n".join(prompt_lines).format(code=current_code)

    parts = []
    if round_idx == 0 or args.repeat_prompt:
        parts.append(main_prompt)
    if round_idx == 0 and args.reference_file:
        reference = args.reference_file.read_text()
        parts.append(f"Here is documentation on the interface for using procedural nodes:\n```python\n{reference}\n```")
    if round_idx == 0 and args.examples_file:
        examples = args.examples_file.read_text()
        parts.append(f"Here are some example shaders for reference:\n```python\n{examples}\n```")
    if round_idx == 0 or args.repeat_goal_image:
        parts.append("Here is the goal image to recreate:")
        parts.append(goal_render)
    
    parts.append(f"Round {round_idx + 1}/{args.rounds}. Here is the result for your current code:")
    if isinstance(last_result, Path):
        parts.append(last_result)
    else:
        assert round_idx != 0
        parts.append(f"Error: {last_result}")

    # Call LLM
    log(f"[SEND]: editing {code_path}")
    if args.model == "dryrun":
        new_code = current_code
        response_text = "Dryrun mode - skipping LLM call"
    elif args.model.startswith("gemini"):
        response_text = call_gemini(client, parts)
        new_code = extract_code(response_text)
    elif args.model.startswith("gpt") or args.model.startswith("o1"):
        response_text = call_openai(client, args.model, parts)
        new_code = extract_code(response_text)
    else:
        raise ValueError(f"Unknown model: {args.model}")

    if response_text is None:
        raise ValueError("LLM returned empty response")
    log(f"[RECV]: {truncate(response_text)!r}")
    new_code = extract_code(response_text)

    # Save step to chat data
    step = {
        "round": round_idx,
        "parts": [str(p) if isinstance(p, Path) else p for p in parts],
        "response": response_text,
    }
    chat_data.append(step)

    def save_chat():
        (output_folder / "chat.json").write_text(json.dumps(chat_data, indent=2))

    if new_code is None:
        msg = "No ```python code block found in response"
        logwarn(f"[PARSE]: {msg} | {code_path.resolve()}")
        save_chat()
        return current_code, msg
    code_path.write_text(new_code)

    # Check for disallowed imports
    import_error = check_imports(new_code)
    if import_error:
        log(f"[IMPORT]: {import_error}")
        save_chat()
        return new_code, import_error

    # Render (with semaphore to limit concurrent renders)
    with render_lock():
        if args.backend == "pf":
            render_result, render_cmd = render_pf(code_path, render_dir, blendfile, n_views)
        elif args.backend == "bgym":
            render_result, render_cmd = render_bgym(
                code_path, render_dir, blendfile, args.blender_path, args.render_script, n_views
            )
        else:
            raise ValueError(f"Unknown backend: {args.backend}")

    step["render_cmd"] = " ".join(render_cmd)
    save_chat()

    if isinstance(render_result, str):
        stderr_path = render_dir / "render_stderr.log"
        log(f"[CRASH]: {truncate(render_result.split(chr(10))[-1], 50)} | {stderr_path}")
        return new_code, render_result

    log(f"[RENDER]: {render_result}")
    return new_code, render_result


def setup_logging(output_folder: Path, loglevel: int):
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    formatter = logging.Formatter("%(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(loglevel)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(output_folder / "log.txt")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bench_data", type=Path, help="Top-level benchmark data folder")
    parser.add_argument("--output_dir", type=Path, help="Top-level output folder")
    parser.add_argument("--prompt_file", type=Path, required=True)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--model", type=str, default="gpt-4o")
    parser.add_argument("--backend", type=str, default="pf", choices=["pf", "bgym"])
    parser.add_argument("--tasks", type=str, nargs="+", default=None, help="Task names to run")
    parser.add_argument("--task_type", type=str, default=None, help="Task type prefix to filter (e.g., material, geometry)")
    parser.add_argument("--workers", type=int, default=1, help="Number of parallel workers")
    parser.add_argument("--max_renders", type=int, default=None, help="Max concurrent renders (default: workers)")
    parser.add_argument(
        "--blender_path", type=Path, default=None, help="Required for bgym backend"
    )
    parser.add_argument(
        "--render_script", type=Path, default=None, help="Required for bgym backend"
    )
    parser.add_argument(
        "--loglevel",
        type=lambda s: getattr(logging, s.upper()),
        default=logging.INFO,
        help="Logging level: DEBUG, INFO, WARNING, ERROR",
    )
    parser.add_argument(
        "--repeat_prompt", type=int, choices=[0, 1], default=1, help="If true, dont repeat the initial prompt every round"
    )
    parser.add_argument("--repeat_goal_image", type=int, choices=[0, 1], default=1, help="If true, dont repeat the goal image every round")
    parser.add_argument(
        "--reference_file", type=Path, default=None,
        help="API reference/interface file to include in first round prompt"
    )
    parser.add_argument(
        "--examples_file", type=Path, default=None,
        help="Example code file to include in first round prompt"
    )
    parser.add_argument(
        "--skip_existing", action="store_true",
        help="Skip tasks that already have completed output"
    )
    parser.add_argument(
        "--api_key_txt", type=Path, default=None,
        help="Path to a text file containing the API key for the model provider"
    )
    return parser


def _infer_api_key_txt(model: str) -> Path | None:
    if model.startswith("gemini"):
        p = Path("credentials/gemini_api.txt")
    elif model.startswith("gpt") or model.startswith("o1"):
        p = Path("credentials/openai_api.txt")
    else:
        return None
    return p if p.exists() else None


def _resolve_api_key(model: str, api_key_txt: Path | None = None) -> tuple[str, str]:
    if api_key_txt is None:
        api_key_txt = _infer_api_key_txt(model)

    if api_key_txt is not None:
        return api_key_txt.read_text().strip(), str(api_key_txt)
    elif model.startswith("gemini"):
        return os.environ["GOOGLE_API_KEY"], "env GOOGLE_API_KEY"
    elif model.startswith("gpt") or model.startswith("o1"):
        return os.environ["OPENAI_API_KEY"], "env OPENAI_API_KEY"
    else:
        raise ValueError(f"Unknown model: {model}")


def init_client(model: str, api_key_txt: Path | None = None):
    if model == "dryrun":
        return None

    api_key, _ = _resolve_api_key(model, api_key_txt)

    if model.startswith("gemini"):
        genai_client = genai.Client(api_key=api_key)
        config = {}
        if "gemini-3" in model:
            config["thinking_config"] = genai.types.ThinkingConfig(thinking_level="low")
        chat = genai_client.chats.create(model=model, config=config)
        return {"client": genai_client, "chat": chat}
    elif model.startswith("gpt") or model.startswith("o1"):
        return {"client": OpenAI(api_key=api_key), "messages": []}
    else:
        raise ValueError(f"Unknown model: {model}")


def get_start(task_folder: Path, task_name: str) -> tuple[str, Path]:
    start_code_path = task_folder / "start.py"
    start_render_dir = task_folder / "renders" / "start"
    code = start_code_path.read_text()
    n_views = get_n_views(task_name)
    render_path = get_render_path(start_render_dir, n_views)
    assert render_path is not None, f"Start render not found in {start_render_dir}"
    return code, render_path


def run_task(args, task_name: str) -> list[dict]:
    """Run inference for a single task. Returns list of crashes."""
    task_folder = args.bench_data / task_name
    output_folder = args.output_dir / task_name
    output_folder.mkdir(parents=True, exist_ok=True)

    # Create task-specific args copy
    task_args = argparse.Namespace(**vars(args))
    task_args.task_folder = None
    task_args.output_folder = None

    client = init_client(args.model, api_key_txt=args.api_key_txt)
    current_code, last_result = get_start(task_folder, task_name)
    chat_data = []
    crashes = []

    for round_idx in range(args.rounds):
        current_code, last_result = run_round(
            task_args, round_idx, client, current_code, last_result, chat_data,
            task_folder, output_folder,
        )
        if isinstance(last_result, str):
            stderr_path = output_folder / f"round_{round_idx:02d}" / "render_stderr.log"
            error_lines = last_result.strip().split("\n")[-10:]
            crashes.append({
                "task": task_name,
                "round": round_idx,
                "error": "\n".join(error_lines),
                "stderr": str(stderr_path),
            })

    logger.info(f"[{task_name}] Done. Results in {output_folder}")
    return crashes


def main():
    args = get_parser().parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for attr in ("bench_data", "output_dir", "prompt_file", "blender_path", "render_script", "reference_file", "examples_file", "api_key_txt"):
        val = getattr(args, attr, None)
        if isinstance(val, Path):
            setattr(args, attr, val.resolve())

    setup_logging(args.output_dir, args.loglevel)
    logger.debug(args)

    if args.model != "dryrun":
        api_key, source = _resolve_api_key(args.model, args.api_key_txt)
        logger.info(f"API key: {len(api_key)} chars from {source}")

    # Get task list
    if args.tasks:
        tasks = args.tasks
    else:
        tasks = sorted([d.name for d in args.bench_data.iterdir() if d.is_dir()])
    if args.task_type:
        tasks = [t for t in tasks if t.startswith(args.task_type)]
    if args.skip_existing:
        def is_complete(task):
            final_round = args.output_dir / task / f"round_{args.rounds - 1:02d}"
            return final_round.exists()
        skipped = [t for t in tasks if is_complete(t)]
        tasks = [t for t in tasks if not is_complete(t)]
        if skipped:
            logger.info(f"Skipping {len(skipped)} existing tasks: {skipped}")
        if not tasks:
            logger.info("All tasks already complete")
            return
    assert tasks, "No tasks to run"

    logger.info(f"Running {len(tasks)} tasks: {tasks}")

    if args.workers == 1:
        all_crashes = []
        for task in tasks:
            all_crashes.extend(run_task(args, task))
    else:
        max_renders = args.max_renders or args.workers
        sem = multiprocessing.Semaphore(max_renders)
        logger.info(f"Max concurrent renders: {max_renders}")
        with multiprocessing.Pool(args.workers, initializer=init_worker, initargs=(sem,)) as pool:
            results = pool.map(partial(run_task, args), tasks)
        all_crashes = [c for crashes in results for c in crashes]

    # Summary
    summary = build_summary(args, tasks, all_crashes)
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2))

    logger.info("\n=== Summary ===")
    logger.info(f"Crash rate: {len(all_crashes)}/{summary['total_rounds']} ({summary['crash_rate']:.1f}%)")
    if all_crashes:
        for c in all_crashes:
            err_short = truncate(c["error"].split("\n")[-1], 50)
            logger.info(f"  {c['task']} r{c['round']}: {err_short} | {c['stderr']}")

    eval_script = Path(__file__).parent / "evaluate_results.py"
    logger.info(f"\nTo evaluate:\nuv run python {eval_script} {args.output_dir} --bench_data {args.bench_data}")


if __name__ == "__main__":
    main()
