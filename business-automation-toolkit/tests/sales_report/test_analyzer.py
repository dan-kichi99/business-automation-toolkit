import pandas as pd
import pytest

from modules.sales_report.analyzer import SalesAnalysisResult, SalesAnalyzer


def make_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-08-01", "2026-08-01", "2026-08-02"]),
            "staff": ["Tanaka", "Sato", "Tanaka"],
            "product": ["Laptop", "Mouse", "Keyboard"],
            "quantity": [1, 2, 1],
            "price": [85000, 3500, 12000],
        }
    )


def metric_value(summary: pd.DataFrame, metric: str):
    return summary.loc[summary["metric"] == metric, "value"].iloc[0]


@pytest.fixture
def analyzer() -> SalesAnalyzer:
    return SalesAnalyzer()


# ---- Core calculations ----


def test_analyze_returns_sales_analysis_result(analyzer):
    result = analyzer.analyze(make_data())

    assert isinstance(result, SalesAnalysisResult)


def test_analyze_adds_sales_column(analyzer):
    result = analyzer.analyze(make_data())

    assert result.detailed["sales"].tolist() == [85000, 7000, 12000]


def test_analyze_total_sales(analyzer):
    result = analyzer.analyze(make_data())

    assert metric_value(result.summary, "total_sales") == 104000


def test_analyze_total_quantity(analyzer):
    result = analyzer.analyze(make_data())

    assert metric_value(result.summary, "total_quantity") == 4


def test_analyze_transaction_count(analyzer):
    result = analyzer.analyze(make_data())

    assert metric_value(result.summary, "transaction_count") == 3


def test_analyze_average_sales_per_transaction(analyzer):
    result = analyzer.analyze(make_data())

    assert metric_value(result.summary, "average_sales_per_transaction") == pytest.approx(
        104000 / 3
    )


# ---- Aggregations ----


def test_analyze_by_staff_aggregation(analyzer):
    result = analyzer.analyze(make_data())

    tanaka = result.by_staff.loc[result.by_staff["staff"] == "Tanaka"].iloc[0]
    sato = result.by_staff.loc[result.by_staff["staff"] == "Sato"].iloc[0]

    assert tanaka["sales"] == 97000
    assert tanaka["quantity"] == 2
    assert tanaka["transaction_count"] == 2

    assert sato["sales"] == 7000
    assert sato["quantity"] == 2
    assert sato["transaction_count"] == 1


def test_analyze_by_product_aggregation(analyzer):
    result = analyzer.analyze(make_data())

    laptop = result.by_product.loc[result.by_product["product"] == "Laptop"].iloc[0]

    assert laptop["sales"] == 85000
    assert laptop["quantity"] == 1
    assert laptop["transaction_count"] == 1


def test_analyze_by_month_aggregation(analyzer):
    result = analyzer.analyze(make_data())

    assert len(result.by_month) == 1
    row = result.by_month.iloc[0]
    assert row["month"] == "2026-08"
    assert row["sales"] == 104000
    assert row["quantity"] == 4
    assert row["transaction_count"] == 3


def test_analyze_by_month_separates_multiple_months(analyzer):
    data = make_data()
    data.loc[len(data)] = [pd.Timestamp("2026-09-01"), "Sato", "Mouse", 1, 3500]

    result = analyzer.analyze(data)

    months = result.by_month["month"].tolist()
    assert months == ["2026-08", "2026-09"]

    september = result.by_month.loc[result.by_month["month"] == "2026-09"].iloc[0]
    assert september["sales"] == 3500
    assert september["quantity"] == 1
    assert september["transaction_count"] == 1


# ---- Immutability / extra columns ----


def test_analyze_does_not_mutate_input(analyzer):
    original = make_data()
    snapshot = original.copy()

    analyzer.analyze(original)

    pd.testing.assert_frame_equal(original, snapshot)
    assert "sales" not in original.columns


def test_analyze_preserves_extra_columns(analyzer):
    data = make_data()
    data["memo"] = ["A", "B", "C"]

    result = analyzer.analyze(data)

    assert "memo" in result.detailed.columns
    assert result.detailed["memo"].tolist() == ["A", "B", "C"]


# ---- Ordering ----


def test_by_staff_sorted_by_sales_desc(analyzer):
    result = analyzer.analyze(make_data())

    assert result.by_staff["staff"].tolist() == ["Tanaka", "Sato"]


def test_by_product_sorted_by_sales_desc(analyzer):
    result = analyzer.analyze(make_data())

    assert result.by_product["product"].tolist() == ["Laptop", "Keyboard", "Mouse"]


def test_by_month_sorted_ascending(analyzer):
    data = make_data()
    data.loc[len(data)] = [pd.Timestamp("2026-07-01"), "Sato", "Mouse", 1, 1000]

    result = analyzer.analyze(data)

    assert result.by_month["month"].tolist() == ["2026-07", "2026-08"]


def test_tie_breaks_by_name_ascending(analyzer):
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-08-01", "2026-08-01"]),
            "staff": ["Bravo", "Alpha"],
            "product": ["Widget", "Widget"],
            "quantity": [1, 2],
            "price": [100, 50],
        }
    )

    result = analyzer.analyze(data)

    assert result.by_staff["staff"].tolist() == ["Alpha", "Bravo"]


# ---- Boundary values ----


def test_price_zero_produces_zero_sales(analyzer):
    data = make_data()
    data.loc[0, "price"] = 0

    result = analyzer.analyze(data)

    assert result.detailed.loc[0, "sales"] == 0


def test_single_row_transaction_count_and_average(analyzer):
    data = make_data().iloc[[0]].reset_index(drop=True)

    result = analyzer.analyze(data)

    assert metric_value(result.summary, "transaction_count") == 1
    assert metric_value(result.summary, "average_sales_per_transaction") == metric_value(
        result.summary, "total_sales"
    )


def test_large_quantity_and_price_does_not_break(analyzer):
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-08-01"]),
            "staff": ["Tanaka"],
            "product": ["Bulk Item"],
            "quantity": [1_000_000],
            "price": [999_999],
        }
    )

    result = analyzer.analyze(data)

    assert result.detailed.loc[0, "sales"] == 1_000_000 * 999_999
    assert metric_value(result.summary, "total_sales") == 1_000_000 * 999_999
