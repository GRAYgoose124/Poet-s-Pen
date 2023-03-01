import logging
import argparse

from pathlib import Path


from .project_creator import ProjectCreator


def parser():
    parser = argparse.ArgumentParser()
    # command group
    subparsers = parser.add_subparsers(dest="command", required=True)

    # new command
    new_parser = subparsers.add_parser("new", help="Create a new project")
    new_parser.add_argument("-rp", "--root_path", help="The path to create the project in", default=Path.cwd())
    new_parser.add_argument("-r", "--recreate", help="Recreate the project if it already exists", action="store_true", default=False)
    new_parser.add_argument("project_name", help="The name of the project to create")

    # run command
    run_parser = subparsers.add_parser("run", help="Run a project")
    run_parser.add_argument("-rp", "--root_path", help="The path where the project is located", default=Path.cwd())
    
    # add dep / remove dep / update dep
    # install / uninstall / update lockfile

    return parser


def main():
    args = parser().parse_args()
    logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s]\t%(message)s")

    pc = ProjectCreator()

    root_path = Path(args.root_path) / "demo"

    match args.command:
        case "new":
            pc.new(root_path, args.project_name, recreate=args.recreate)
        case "run":
            pc.setup(root_path).run()


if __name__ == "__main__":
    main()
