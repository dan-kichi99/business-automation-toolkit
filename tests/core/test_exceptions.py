from core.exceptions import (
    BusinessAutomationError,
    ExportError,
    FileReadError,
    ValidationError,
)


def test_validation_error_is_business_automation_error():
    assert issubclass(ValidationError, BusinessAutomationError)


def test_file_read_error_is_business_automation_error():
    assert issubclass(FileReadError, BusinessAutomationError)


def test_export_error_is_business_automation_error():
    assert issubclass(ExportError, BusinessAutomationError)
