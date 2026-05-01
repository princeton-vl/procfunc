import argparse

from procfunc.transpiler import main as transpiler_main
from procfunc.util.teardown import skip_teardown_on_exit


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="procfunc")
    subparsers = parser.add_subparsers(dest="command", required=True)

    transpile_parser = subparsers.add_parser(
        "transpile", help="Transpile a Blender file to procfunc Python code."
    )
    transpiler_main.add_transpile_arguments(transpile_parser)

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    if args.command == "transpile":
        transpiler_main.run(args)
    else:
        parser.error(f"Unknown command: {args.command}")


def cli():
    with skip_teardown_on_exit():
        main()


if __name__ == "__main__":
    cli()
