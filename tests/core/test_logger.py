from core.logger import get_logger


def test_get_logger_returns_logger():
    logger = get_logger("test_logger")
    assert logger.name == "test_logger"


def test_get_logger_does_not_duplicate_handlers():
    logger1 = get_logger("duplicate_test")
    logger2 = get_logger("duplicate_test")
    assert logger1 is logger2
    assert len(logger1.handlers) == 1
