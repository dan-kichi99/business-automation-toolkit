from dataclasses import dataclass

import pandas as pd


@dataclass
class SalesAnalysisResult:
    detailed: pd.DataFrame
    summary: pd.DataFrame
    by_staff: pd.DataFrame
    by_product: pd.DataFrame
    by_month: pd.DataFrame


class SalesAnalyzer:
    def analyze(self, data: pd.DataFrame) -> SalesAnalysisResult:
        detailed = data.copy()
        detailed["sales"] = detailed["quantity"] * detailed["price"]

        return SalesAnalysisResult(
            detailed=detailed,
            summary=self._build_summary(detailed),
            by_staff=self._build_group_summary(detailed, "staff"),
            by_product=self._build_group_summary(detailed, "product"),
            by_month=self._build_month_summary(detailed),
        )

    def _build_summary(self, detailed: pd.DataFrame) -> pd.DataFrame:
        total_sales = int(detailed["sales"].sum())
        total_quantity = int(detailed["quantity"].sum())
        transaction_count = len(detailed)
        average_sales_per_transaction = total_sales / transaction_count

        return pd.DataFrame(
            {
                "metric": [
                    "total_sales",
                    "total_quantity",
                    "transaction_count",
                    "average_sales_per_transaction",
                ],
                "value": pd.Series(
                    [
                        total_sales,
                        total_quantity,
                        transaction_count,
                        average_sales_per_transaction,
                    ],
                    dtype=object,
                ),
            }
        )

    def _build_group_summary(self, detailed: pd.DataFrame, group_column: str) -> pd.DataFrame:
        grouped = (
            detailed.groupby(group_column)
            .agg(
                sales=("sales", "sum"),
                quantity=("quantity", "sum"),
                transaction_count=("sales", "size"),
            )
            .reset_index()
        )
        return grouped.sort_values(
            ["sales", group_column], ascending=[False, True]
        ).reset_index(drop=True)

    def _build_month_summary(self, detailed: pd.DataFrame) -> pd.DataFrame:
        working = detailed.assign(month=detailed["date"].dt.strftime("%Y-%m"))
        grouped = (
            working.groupby("month")
            .agg(
                sales=("sales", "sum"),
                quantity=("quantity", "sum"),
                transaction_count=("sales", "size"),
            )
            .reset_index()
        )
        return grouped.sort_values("month", ascending=True).reset_index(drop=True)
