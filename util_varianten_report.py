import pathlib


class VarianteResults:
    def __init__(self, directory: pathlib.Path):
        assert isinstance(directory, pathlib.Path)
        self._filename = directory / "variante_results.txt"

    def exists(self) -> bool:
        return self._filename.exists()

    def write(self, label: str, value: float) -> None:
        assert isinstance(label, str)
        assert isinstance(value, float)

        with self._filename.open("a") as f:
            f.write(f"{label}={value}\n")
