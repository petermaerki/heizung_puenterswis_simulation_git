import logging
import pathlib

logger = logging.getLogger("simulation")

DIRECTORY_TOP = pathlib.Path(__file__).resolve().parent
DIRECTORY_REPORTS = DIRECTORY_TOP / "reports"
DIRECTORY_RESULTS = DIRECTORY_TOP / "test_speicher_dezentral-results"
DIRECTORY_RESULTS.mkdir(exist_ok=True)


def remove_files(directory: pathlib.Path):
    """
    Remove all files in DIRECTORY_REPORTS if possible
    """
    for filename in directory.rglob("*.*"):
        try:
            filename.unlink()
        except Exception as e:
            print(f"DEBUG: Failed to remove {filename.relative_to(DIRECTORY_TOP) }")


LOGGING_FORMAT = "%(filename)s:%(lineno)s %(funcName)s() %(levelname)s %(message)s"


def init_logging(directory: pathlib.Path = None):
    if directory is None:
        directory = DIRECTORY_TOP
    filename = directory / "simulation_logging.txt"

    # Remove previous handlers
    while len(logging.root.handlers) > 0:
        logger.removeHandler(logging.root.handlers[0])

    formatter = logging.Formatter(LOGGING_FORMAT)

    fh = logging.FileHandler(filename=filename)
    fh.setLevel(level=logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(level=logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.setLevel(level=logging.INFO)
