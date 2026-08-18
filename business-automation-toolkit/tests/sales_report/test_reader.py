import pandas as pd
import pytest

from core.exceptions import FileReadError
from modules.sales_report.reader import SalesDataReader

CSV_CONTENT = (
    "date,staff,product,quantity,price\n"
    "2026-08-01,Tanaka,Laptop,1,85000\n"
    "2026-08-01,Sato,Mouse,2,3500\n"
)
COLUMNS = ["date", "staff", "product", "quantity", "price"]


@pytest.fixture
def reader() -> SalesDataReader:
    return SalesDataReader()


def test_read_csv_returns_dataframe(reader, tmp_path):
    csv_path = tmp_path / "sales.csv"
    csv_path.write_text(CSV_CONTENT, encoding="utf-8")

    result = reader.read(csv_path)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert list(result.columns) == COLUMNS


def test_read_xlsx_returns_dataframe(reader, tmp_path):
    xlsx_path = tmp_path / "sales.xlsx"
    expected = pd.DataFrame(
        {
            "date": ["2026-08-01", "2026-08-01"],
            "staff": ["Tanaka", "Sato"],
            "product": ["Laptop", "Mouse"],
            "quantity": [1, 2],
            "price": [85000, 3500],
        }
    )
    expected.to_excel(xlsx_path, index=False)

    result = reader.read(xlsx_path)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert list(result.columns) == COLUMNS


def test_read_cp932_csv_preserves_japanese_characters(reader, tmp_path):
    csv_path = tmp_path / "sales_cp932.csv"
    content = "date,staff,product,quantity,price\n2026-08-01,田中,ノートパソコン,1,85000\n"
    csv_path.write_bytes(content.encode("cp932"))

    result = reader.read(csv_path)

    assert result.loc[0, "staff"] == "田中"
    assert result.loc[0, "product"] == "ノートパソコン"


def test_read_missing_file_raises_file_read_error(reader, tmp_path):
    missing_path = tmp_path / "missing.csv"

    with pytest.raises(FileReadError):
        reader.read(missing_path)


def test_read_directory_raises_file_read_error(reader, tmp_path):
    with pytest.raises(FileReadError):
        reader.read(tmp_path)


def test_read_unsupported_extension_raises_file_read_error(reader, tmp_path):
    txt_path = tmp_path / "sales.txt"
    txt_path.write_text("not a csv", encoding="utf-8")

    with pytest.raises(FileReadError):
        reader.read(txt_path)


def test_read_broken_csv_raises_file_read_error(reader, tmp_path):
    csv_path = tmp_path / "broken.csv"
    csv_path.write_text('a,b\n"unterminated,1\n', encoding="utf-8")

    with pytest.raises(FileReadError):
        reader.read(csv_path)


def test_read_broken_xlsx_raises_file_read_error(reader, tmp_path):
    xlsx_path = tmp_path / "broken.xlsx"
    xlsx_path.write_text("this is not a real xlsx file", encoding="utf-8")

    with pytest.raises(FileReadError):
        reader.read(xlsx_path)
