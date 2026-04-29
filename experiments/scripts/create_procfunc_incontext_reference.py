import argparse
from pathlib import Path


def blank_function_body(
    lines: list[str],
    fnname: str,
    delete_all: bool = False,
    keep_return: bool = False,
):
    start = [
        i for i, line in enumerate(lines)
        if line.split("(")[0] == f"def {fnname}"
    ]
    if len(start) != 1:
        fns = [lines[i] for i in start]
        raise ValueError(f"Expected 1 function definition for {fnname!r}, got {len(fns)}: \n\t{fns}")
    i = start[0]

    if delete_all:
        while not lines[i].strip().endswith(":"):
            lines.pop(i)
        if lines[i - 1].startswith("@"):
            lines[i - 1] = ""
        lines.pop(i)
    else:
        while not lines[i].endswith(":"):
            i += 1
        i += 1

    while i < len(lines) and (
        lines[i].startswith(" ")
        or lines[i].startswith("\t")
        or lines[i] == ""
    ):
        if keep_return and lines[i].strip().startswith("return"):
            break
        lines.pop(i)

    if not delete_all and not keep_return:
        lines.insert(i, "    pass")


def modify(lines):
    header_end = next(
        i for i, line in enumerate(lines) 
        if line == "" and lines[i+1] == ""
    )

    lines = lines[header_end:]

    # remove block commented stuff
    i = 0
    def iscomment(line):
        return line.startswith("'''") or line.startswith('"""')
    while i < len(lines):
        if iscomment(lines[i]):
            lines.pop(i)
            while not iscomment(lines[i]):
                lines.pop(i)
            lines.pop(i)
        else:
            i += 1
        
    # remove all fn impls
    names = [
        line.removeprefix("def ").split("(")[0]
        for line in lines if line.startswith("def ")
    ]
    for i, name in enumerate(names):
        blank_function_body(lines, name, delete_all=name.startswith("_"))

    return lines

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output_path", type=Path)
    parser.add_argument("input_paths", type=Path, nargs="+")
    args = parser.parse_args()

    ifg_path = Path()/".."/"src"
    assert ifg_path.exists(), f"Expected to find infinigen at {ifg_path}"

    lines = []
    for input_path in args.input_paths:
        module_path = str(input_path.relative_to(ifg_path)).split(".")[0].replace("/", ".")
        lines.append(f"\n###MODULE {module_path}")
        lines += modify(input_path.read_text().splitlines())

    text = "\n".join(lines)
    
    # make the typing look like an external user's view, not the implementation view
    text = text.replace("pt.", "pf.")
    text = text.replace("nt.", "pf.")

    if args.output_path.exists():
        args.output_path.unlink()
    args.output_path.write_text(text)

if __name__ == "__main__":
    main()


