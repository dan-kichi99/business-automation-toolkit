from pathlib import Path
from zipfile import BadZipFile

import pandas as pd

from core.exceptions import FileReadError
from core.logger import get_logger

logger = get_logger(__name__)

SUPPORTED_EXTENSIONS = (".csv", ".xlsx")


class SalesDataReader:
    def read(self, file_path: str | Path) -> pd.DataFrame:
        path = Path(file_path)

        if not path.exists():
            raise FileReadError(f"File does not exist: {file_path}")

        if not path.is_file():
            raise FileReadError(
                f"Expected a file but received a directory: {file_path}"
            )

        suffix = path.suffix.lower()

        if suffix == ".csv":
            return self._read_csv(path)
        if suffix == ".xlsx":
            return self._read_excel(path)

        raise FileReadError(
            f"Unsupported file format: {suffix}. "
            f"Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    def _read_csv(self, path: Path) -> pd.DataFrame:
        try:
            return pd.read_csv(path, encoding="utf-8")
        except UnicodeDecodeError:
            logger.info("UTF-8 decoding failed for %s, retrying with CP932", path)
            try:
                return pd.read_csv(path, encoding="cp932")
            except (UnicodeDecodeError, pd.errors.ParserError, OSError) as exc:
                logger.exception("Failed to read CSV file with CP932: %s", path)
                raise FileReadError(f"Failed to read CSV file: {path.name}") from exc
        except (pd.errors.ParserError, OSError, ValueError) as exc:
            logger.exception("Failed to read CSV file: %s", path)
            raise FileReadError(f"Failed to read CSV file: {path.name}") from exc

    def _read_excel(self, path: Path) -> pd.DataFrame:
        try:
            return pd.read_excel(path)
        except (ValueError, OSError, BadZipFile) as exc:
            logger.exception("Failed to read Excel file: %s", path)
            raise FileReadError(f"Failed to read Excel file: {path.name}") from exc
