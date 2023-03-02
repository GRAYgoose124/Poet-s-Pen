import logging
import argparse

from pathlib import Path


from .project_creator import ProjectCreator


def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-rp", "--root_path", help="The path where the project is located", default=Path.cwd())

    # command group
    cmd_parsers = parser.add_subparsers(dest="command", required=True)

    # new command
    new_parser = cmd_parsers.add_parser("new", help="Create a new project")
    new_parser.add_argument("-r", "--recreate", help="Recreate the project if it already exists", action="store_true", default=False)
    new_parser.add_argument("project_name", help="The name of the project to create")

    # poetry commands command
    poetry_subparser = cmd_parsers.add_parser("poetry", help="Run a poetry command on the project at the given root path")
    poetry_subparser.add_argument("poetry_command", help="The poetry command to run")
    poetry_subparser.add_argument("poetry_args", nargs="*", help="The arguments to pass to the poetry command")
    poetry_subparser.add_argument("-pt", "--poetry_pass_through", help="Pass the arguments through to the poetry command without any pre-processing", action="store_true", default=False)
    
    # add dep / remove dep / update dep
    # install / uninstall / update lockfile

    return parser


def main():
    args = parser().parse_args()
    logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s]\t%(message)s")

    pc = ProjectCreator()

    root_path = Path(args.root_path)

    match args.command:
        case "new":
            pc.new(root_path, args.project_name, recreate=args.recreate)
        case "poetry":
            pc.setup(root_path).poetry_command(args.poetry_command, *args.poetry_args, managed=not args.poetry_pass_through)


if __name__ == "__main__":
    main()
