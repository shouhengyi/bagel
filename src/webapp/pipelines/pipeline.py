"""Classes and functions to manage pipeline definitions."""

import pathlib
from typing import Annotated

from pydantic import AfterValidator, BaseModel

from settings import settings
from src.command.run import validate


def _validate_name(s: str) -> str:
    validate.validate_snake_case(s)
    return s


class Pipeline(BaseModel):
    """Represent a pipeline definition file."""

    name: Annotated[str, AfterValidator(_validate_name)]
    content: str = ""

    @property
    def file(self) -> pathlib.Path:
        """Return the pipeline definition file path."""
        return pathlib.Path(settings.PIPELINE_DEFINITION_DIRECTORY) / f"{self.name}.yaml"

    def save(self) -> None:
        """Save the content to the pipeline file."""
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.file.write_text(self.content, encoding="utf-8")


def list_() -> list[Pipeline]:
    """List all pipeline definitions."""
    files = pathlib.Path(settings.PIPELINE_DEFINITION_DIRECTORY).glob("*.yaml")
    return [Pipeline(name=file.stem, file=file) for file in files]


def exists(name: str) -> bool:
    """Check if a pipeline with the given name exists."""
    return pathlib.Path(settings.PIPELINE_DEFINITION_DIRECTORY, f"{name}.yaml").exists()
