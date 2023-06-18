import logging
import pathlib

_logger = logging.getLogger("simulation")

DIRECTORY_TOP = pathlib.Path(__file__).resolve().parent
DIRECTORY_REPORTS = DIRECTORY_TOP / "reports"
DIRECTORY_RESULTS = DIRECTORY_TOP / "test_speicher_dezentral-results"
DIRECTORY_RESULTS.mkdir(exist_ok=True)

SAVEFIG_KWARGS = dict(metadata={})


def warning(logger: logging.Logger, time_s: float, msg: str):
    """
    Vor dem Zeitpunkt 0 werden warnungen als 'debug' ausgegeben, nachher als 'warnung'.
    Zudem wird der Meldung noch der Zeitpunkt beigefügt.
    """
    func = logger.warning if time_s > 0.0 else logger.debug
    func(f"{time_s/3600.0:0.1f}h: {msg}")


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
    while len(_logger.handlers) > 0:
        _logger.removeHandler(_logger.handlers[0])

    formatter = logging.Formatter(LOGGING_FORMAT)

    fh = logging.FileHandler(filename=filename)
    fh.setLevel(level=logging.DEBUG)
    fh.setFormatter(formatter)
    _logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(level=logging.INFO)
    ch.setFormatter(formatter)
    _logger.addHandler(ch)

    _logger.setLevel(level=logging.DEBUG)
