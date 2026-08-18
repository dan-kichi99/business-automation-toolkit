from core.result import Result


def test_success_result():
    result = Result(success=True, message="OK")
    assert result.success is True
    assert result.message == "OK"


def test_failure_result():
    result = Result(success=False, message="Failed")
    assert result.success is False
    assert result.message == "Failed"
