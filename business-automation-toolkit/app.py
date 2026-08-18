from core.logger import get_logger
from gui.main_window import launch

logger = get_logger(__name__)


def main() -> None:
    logger.info("Starting Business Automation Toolkit")
    try:
        launch()
    except Exception:
        logger.exception("Unexpected error occurred")


if __name__ == "__main__":
    main()
