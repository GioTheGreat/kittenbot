from pathlib import Path
from typing import Protocol, TypeVar

from attr import define

from .random_generator import RandomGenerator

T = TypeVar("T")


class Resources(Protocol[T]):
    def get_random_resource(self, directory: str) -> T:
        pass


class Resource(Protocol):
    name: str

    def get_bytes(self) -> bytes:
        pass


@define
class ProdResource(Resources):
    name: str
    path: Path

    def get_bytes(self) -> bytes:
        with open(self.path, "rb") as f:
            return f.read()


@define
class ProdResources(Resources[ProdResource]):
    random_generator: RandomGenerator
    base_dir: str

    def get_random_resource(self, directory: str) -> ProdResource:
        resources_path = Path(self.base_dir, directory)
        all_resources = list(resources_path.glob("*"))
        selected_resource = self.random_generator.choice(all_resources)
        return ProdResource(selected_resource.name, selected_resource)
