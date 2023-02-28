import logging
from pathlib import Path

from poetry.factory import Factory
from poetry.installation.installer import Installer
from poetry.utils.env import EnvManager
from cleo.io.buffered_io import BufferedIO


logger = logging.getLogger(__name__)


class ProjectCreator:
    def __init__(self) -> None:
        pass

    @staticmethod
    def create(project_path: str) -> None:
        # this man is a godsend: https://github.com/python-poetry/poetry/issues/1053#issuecomment-935758339
        poetry = Factory().create_poetry(Path(project_path))

        ioo = BufferedIO()
        env = EnvManager(poetry).create_venv(ioo)
        logger.debug(f"Using env: {env.path}")

        installer = Installer(
            ioo,
            env,
            poetry.package,
            poetry.locker,
            poetry.pool,
            poetry.config,
        )

        installer.update(True)
        installer.run()

        print(ioo.fetch_output())