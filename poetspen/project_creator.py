import logging
import os
import tomlkit

from pathlib import Path
import shutil
from subprocess import run
from typing import Literal

from poetry.factory import Factory
from poetry.installation.installer import Installer
from poetry.utils.env import EnvManager

from cleo.io.buffered_io import BufferedIO

logger = logging.getLogger(__name__)


class ProjectCreator:
    """ Poetry project helper class. """
    def __init__(self) -> None:
        # Poetry handles
        self._poetry = None
        self._io = None
        self._installer = None

        # Project
        self.__pyproject = None

    def setup(self, project_path: Path):
        """Initialize a Poetry project and return a ProjectCreator instance."""
        # see: https://github.com/python-poetry/poetry/issues/1053#issuecomment-935758339
        poetry = Factory().create_poetry(project_path)
        io = BufferedIO()
        installer = Installer(
            io,
            EnvManager(poetry).create_venv(io),
            poetry.package,
            poetry.locker,
            poetry.pool,
            poetry.config,
        )

        self._poetry = poetry
        self._io = io
        self._installer = installer

        logger.info(f"Initialized Poetry project in {project_path}! Project name: {poetry.package.name}")

        return self

    @staticmethod
    def _new_poetry_project(root_path: Path, project_name: str, recreate: bool = False) -> 'ProjectCreator':
        """Create a new poetry project and return a ProjectCreator instance."""
        # if a project already exists, don't create it
        project_path = root_path / project_name
        if not recreate:
            if (project_path / "pyproject.toml").exists():
                raise FileExistsError(f"\n\tProject already exists at {project_path}!\n\t\tPlease use `-r` or `--recreate` to recreate the project.")
        else:
            if project_path.exists():
                logger.warning(f"Removing existing project at {project_path}!")
                shutil.rmtree(project_path)


        if not root_path.exists():
            root_path.mkdir(parents=True)

        # TODO: Do this properly with the poetry API.
        results = run(["poetry", "new", project_name], cwd=root_path)

        if results.returncode != 0:
            logger.error("Failed to create project with poetry!")
            return
        
        return ProjectCreator().setup(project_path)
    

    def _add_template_files(self, templates: list[str] = ["default", "pytest"]):
        """Add template files to the project."""
        # Add template files
        template_path = Path(__file__).parent.parent / "templates"

        # template filename: templates/{file.ext}-{label}.template
        copied = []
        # glob all files recursively in template_path
        for file in template_path.glob("**/*"):
            if file.name.endswith(".template"):
                file_name, label = file.name.split("-")
                label = label.split(".")[0]

                if label in templates and file_name not in copied:                    
                    if file.parent.name == "tests":
                        print(file)
                        logger.debug(f"Saving test file...")
                        new_path = self._poetry.file.parent / "tests" / file_name
                    if file.parent.name == "package":
                        logger.debug(f"Saving package file...")
                        new_path = self._poetry.file.parent / self._poetry.package.name / file_name
                    else:
                        logger.debug(f"Saving file...")
                        new_path = self._poetry.file.parent / file_name

                    logger.debug(f"\tCopying {file_name} to {new_path}...")
                    shutil.copyfile(file, new_path)

                    copied.append(file_name)

        logger.info(f"Copied template files: {', '.join(copied)}")

    def add_item(self, key: str, value: str):
        """ Add an item to the pyproject.toml file."""
        pyproject_file = self._poetry.file.parent / "pyproject.toml"
        pyproject_toml = tomlkit.parse(self._poetry.file.read_text())

        logger.debug(f"Updating pyproject.toml... {key} = {value}")
        for k, v in value.items():
            if k in pyproject_toml[key]:
                pyproject_toml[key][k].update(v)
            else:
                pyproject_toml[key][k] = v

        logger.debug(f"Writing pyproject.toml...")
        pyproject_file.write_text(tomlkit.dumps(pyproject_toml))

    @staticmethod
    def new(root_path: Path, project_name: str, recreate: bool = False) -> 'ProjectCreator':
        """ Create a new project and return a ProjectCreator instance."""
        # Generate base project
        project = ProjectCreator._new_poetry_project(root_path, project_name, recreate=recreate)

        # Add template files
        project._add_template_files()

        # Add default entrypoint to pyproject.toml # TODO: Use the poetry API for this
        project.add_item("tool", {"poetry": {"scripts": {project_name: f"{project_name}:main"}}})


        return project

    def run(self):
        results = run(["poetry", "run"], cwd=self._poetry.file.parent)

    def install(self, update: bool = False) -> None:
        if update:
            self._installer.update(True)
            
        self._installer.run()
