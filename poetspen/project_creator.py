import logging
import os

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
    def __init__(self) -> None:
        self._poetry = None
        self._io = None
        self._installer = None

    def setup(self, project_path: Path):
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
    def new(root_path: Path, project_name: str, recreate: bool = False) -> 'ProjectCreator':
        # if a project already exists, don't create it
        project_path = root_path / project_name
        if not recreate:
            if (project_path / "pyproject.toml").exists():
                logger.error(f"Project already exists at {project_path}!")
                return
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

    def run(self):
        results = run(["poetry", "run"], cwd=self._poetry.file.parent)

    def install(self, update: bool = False) -> None:
        if update:
            self._installer.update(True)
            
        self._installer.run()
