import pandas as pd
import pytest

from core.exceptions import ValidationError
from modules.sales_report.validator import SalesDataValidator


def make_valid_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2026-08-01", "2026-08-02"],
            "staff": ["Tanaka", "Sato"],
            "product": ["Laptop", "Mouse"],
            "quantity": [1, 2],
            "price": [85000, 3500],
        }
    )


@pytest.fixture
def validator() -> SalesDataValidator:
    return SalesDataValidator()


# ---- Normal cases ----


def test_validate_returns_dataframe_for_valid_data(validator):
    result = validator.validate(make_valid_data())

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2


def test_validate_does_not_mutate_original_dataframe(validator):
    original = make_valid_data()
    snapshot = original.copy()

    validator.validate(original)

    pd.testing.assert_frame_equal(original, snapshot)


def test_validate_preserves_extra_columns(validator):
    data = make_valid_data()
    data["memo"] = ["A", "B"]

    result = validator.validate(data)

    assert "memo" in result.columns
    assert result["memo"].tolist() == ["A", "B"]


def test_validate_converts_date_strings_to_datetime(validator):
    result = validator.validate(make_valid_data())

    assert pd.api.types.is_datetime64_any_dtype(result["date"])


def test_validate_converts_quantity_string_to_int(validator):
    data = make_valid_data()
    data["quantity"] = ["3", "2"]

    result = validator.validate(data)

    assert result["quantity"].tolist() == [3, 2]


def test_validate_converts_price_string_to_int(validator):
    data = make_valid_data()
    data["price"] = ["3500", "1000"]

    result = validator.validate(data)

    assert result["price"].tolist() == [3500, 1000]


def test_validate_strips_whitespace_from_staff(validator):
    data = make_valid_data()
    data["staff"] = [" Tanaka ", "Sato"]

    result = validator.validate(data)

    assert result["staff"].tolist() == ["Tanaka", "Sato"]


def test_validate_allows_price_zero(validator):
    data = make_valid_data()
    data["price"] = [0, 3500]

    result = validator.validate(data)

    assert result["price"].tolist() == [0, 3500]


# ---- Abnormal cases: structural ----


def test_validate_empty_dataframe_raises_validation_error(validator):
    with pytest.raises(ValidationError):
        validator.validate(pd.DataFrame())


def test_validate_zero_records_raises_validation_error(validator):
    data = pd.DataFrame(columns=["date", "staff", "product", "quantity", "price"])

    with pytest.raises(ValidationError):
        validator.validate(data)


def test_validate_missing_single_required_column_raises_validation_error(validator):
    data = make_valid_data().drop(columns=["price"])

    with pytest.raises(ValidationError, match="price"):
        validator.validate(data)


def test_validate_missing_multiple_required_columns_lists_all(validator):
    data = make_valid_data().drop(columns=["price", "quantity"])

    with pytest.raises(ValidationError) as exc_info:
        validator.validate(data)

    assert "price" in str(exc_info.value)
    assert "quantity" in str(exc_info.value)


# ---- Abnormal cases: date ----


def test_validate_invalid_date_raises_validation_error(validator):
    data = make_valid_data()
    data["date"] = ["not-a-date", "2026-08-02"]

    with pytest.raises(ValidationError):
        validator.validate(data)


def test_validate_missing_date_raises_validation_error(validator):
    data = make_valid_data()
    data["date"] = [None, "2026-08-02"]

    with pytest.raises(ValidationError):
        validator.validate(data)


# ---- Abnormal cases: staff / product ----


def test_validate_empty_staff_raises_validation_error(validator):
    data = make_valid_data()
    data["staff"] = ["", "Sato"]

    with pytest.raises(ValidationError):
        validator.validate(data)


def test_validate_whitespace_only_staff_raises_validation_error(validator):
    data = make_valid_data()
    data["staff"] = ["   ", "Sato"]

    with pytest.raises(ValidationError):
        validator.validate(data)


def test_validate_missing_product_raises_validation_error(validator):
    data = make_valid_data()
    data["product"] = [None, "Mouse"]

    with pytest.raises(ValidationError):
        validator.validate(data)


# ---- Abnormal cases: quantity / price boundary values ----


@pytest.mark.parametrize(
    ("column", "value"),
    [
        ("quantity", "abc"),
        ("quantity", 0),
        ("quantity", -1),
        ("quantity", 1.5),
        ("quantity", None),
        ("quantity", float("inf")),
        ("quantity", True),
        ("price", "abc"),
        ("price", -100),
        ("price", 99.5),
        ("price", None),
    ],
)
def test_validate_rejects_invalid_numeric_values(validator, column, value):
    data = make_valid_data()
    data[column] = pd.Series([value, data[column].iloc[1]], dtype=object)

    with pytest.raises(ValidationError):
        validator.validate(data)
