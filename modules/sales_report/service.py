from pathlib import Path

from core.logger import get_logger
from modules.sales_report.analyzer import SalesAnalyzer
from modules.sales_report.exporter import SalesReportExporter
from modules.sales_report.reader import SalesDataReader
from modules.sales_report.validator import SalesDataValidator

logger = get_logger(__name__)


class SalesReportService:
    def __init__(
        self,
        reader: SalesDataReader | None = None,
        validator: SalesDataValidator | None = None,
        analyzer: SalesAnalyzer | None = None,
        exporter: SalesReportExporter | None = None,
    ) -> None:
        self._reader = reader or SalesDataReader()
        self._validator = validator or SalesDataValidator()
        self._analyzer = analyzer or SalesAnalyzer()
        self._exporter = exporter or SalesReportExporter()

    def generate(self, input_path: str | Path, output_path: str | Path) -> Path:
        logger.info("Reading sales data")
        data = self._reader.read(input_path)

        logger.info("Validating sales data")
        validated = self._validator.validate(data)

        logger.info("Analyzing sales data")
        result = self._analyzer.analyze(validated)

        logger.info("Exporting sales report")
        report_path = self._exporter.export(result, output_path)

        logger.info("Sales report generated")
        return report_path
