import logging

from .project_creator import ProjectCreator


def main():
    logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s]\t%(message)s")
    
    pc = ProjectCreator()
    pc.create("asdf")


if __name__ == "__main__":
    main()
