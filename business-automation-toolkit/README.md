# Business Automation Toolkit

## Overview

## Features

Sales Report - Implemented

- CSV / XLSX sales data loading (UTF-8 / CP932 CSV support)
- Sales data validation (required columns: `date`, `staff`, `product`, `quantity`, `price`)
- Sales calculation, staff / product / monthly aggregation
- Excel report generation (Summary / Detailed / Staff / Products / Monthly sheets)
- Desktop GUI (select input file, select output file, Generate Report)

## Architecture

## Requirements

## Installation

## Usage

Run the desktop app:

```bash
python app.py
```

1. Select a CSV or XLSX sales data file (Browse)
2. Select an output `.xlsx` path (Save As)
3. Click Generate Report

### Programmatic Usage

```python
from modules.sales_report.service import SalesReportService

service = SalesReportService()

report_path = service.generate(
    "samples/sales.csv",
    "output/sales_report.xlsx",
)

print(report_path)
```

## Testing

## Project Structure

## Screenshot

## Roadmap

- Sales Report - Completed
- PDF Organizer - Planned
- Excel Formatter - Planned
- File Renamer - Planned
