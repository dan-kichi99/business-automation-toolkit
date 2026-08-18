import math

import numpy as np
import pandas as pd

from core.exceptions import ValidationError

REQUIRED_COLUMNS = ["date", "staff", "product", "quantity", "price"]
TEXT_COLUMNS = ["staff", "product"]
_NUMERIC_TYPES = (int, float, np.integer, np.floating)
_BOOL_TYPES = (bool, np.bool_)


class SalesDataValidator:
    def validate(self, data: pd.DataFrame) -> pd.DataFrame:
        if data.empty:
            raise ValidationError("Sales data is empty.")

        missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
        if missing:
            raise ValidationError(f"Missing required columns: {', '.join(missing)}")

        validated = data.copy()

        self._validate_dates(validated)
        for column in TEXT_COLUMNS:
            self._validate_text_column(validated, column)
        self._validate_numeric_column(validated, "quantity", minimum=1)
        self._validate_numeric_column(validated, "price", minimum=0)

        return validated

    def _validate_dates(self, validated: pd.DataFrame) -> None:
        converted = pd.to_datetime(validated["date"], errors="coerce", format="mixed")

        for position, (raw, value) in enumerate(zip(validated["date"], converted, strict=True)):
            if pd.isna(value):
                row = position + 2
                if pd.isna(raw):
                    raise ValidationError(f"Missing date at row {row}")
                raise ValidationError(f"Invalid date at row {row}: {raw}")

        validated["date"] = converted

    def _validate_text_column(self, validated: pd.DataFrame, column: str) -> None:
        column_index = validated.columns.get_loc(column)

        for position, value in enumerate(validated[column]):
            row = position + 2
            if pd.isna(value):
                raise ValidationError(f"Missing {column} at row {row}")

            text = str(value).strip()
            if not text:
                raise ValidationError(f"Empty {column} at row {row}")

            validated.iat[position, column_index] = text

    def _validate_numeric_column(
        self, validated: pd.DataFrame, column: str, *, minimum: int
    ) -> None:
        normalized = [
            self._validate_numeric_value(value, column, position + 2, minimum)
            for position, value in enumerate(validated[column])
        ]
        validated[column] = normalized

    def _validate_numeric_value(self, value, column: str, row: int, minimum: int) -> int:
        if isinstance(value, _BOOL_TYPES):
            raise ValidationError(f"Invalid {column} at row {row}: {value}")

        if pd.isna(value):
            raise ValidationError(f"Missing {column} at row {row}")

        if isinstance(value, str):
            try:
                numeric = float(value.strip())
            except ValueError as exc:
                raise ValidationError(f"Invalid {column} at row {row}: {value}") from exc
        elif isinstance(value, _NUMERIC_TYPES):
            numeric = float(value)
        else:
            raise ValidationError(f"Invalid {column} at row {row}: {value}")

        if not math.isfinite(numeric):
            raise ValidationError(f"Invalid {column} at row {row}: {value}")

        if not numeric.is_integer():
            raise ValidationError(f"{column} must be a whole number at row {row}: {value}")

        int_value = int(numeric)

        if int_value < minimum:
            if minimum <= 0:
                raise ValidationError(f"{column} must not be negative at row {row}: {value}")
            raise ValidationError(f"{column} must be positive at row {row}: {value}")

        return int_value
