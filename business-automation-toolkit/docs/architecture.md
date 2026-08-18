# Architecture

## Layers

```
GUI
 |
 v
Service Layer
 |
 v
Business Modules
 |
 v
Core Utilities
```

Service Layer here means a per-module orchestration class (e.g.
`SalesReportService`) that calls existing business-module components in the
right order. The GUI depends only on its module's Service class, never on
the lower-level Reader / Validator / Analyzer / Exporter components
directly.

## Responsibilities

- `core/` contains only common utilities shared across business automation
  modules (exceptions, logging, paths, result type). It must never contain
  business-specific logic.
- `modules/` contains business-specific logic, one subpackage per automation
  feature (e.g. `sales_report`).
- `gui/` is display only. It must not contain business logic.
- `app.py` is the application entry point only. It wires up the logger and
  launches the GUI; it contains no business logic.

## Separation of concerns

Business logic and GUI are kept separate so that business modules can be
tested independently of tkinter, and so the GUI can be replaced or extended
without touching business logic.

## Sales Report data flow (current, MVP)

```
User
 |
 v
Tkinter GUI
 |
 v
SalesReportService
 |
 v
SalesDataReader
 |
 v
SalesDataValidator
 |
 v
SalesAnalyzer
 |
 v
SalesReportExporter
 |
 v
Excel Report
```

`SalesDataReader` only loads `.csv` / `.xlsx` files into a DataFrame.
`SalesDataValidator` only checks and normalizes that DataFrame.
`SalesAnalyzer` only calculates the `sales` column and aggregates it into a
`SalesAnalysisResult` (detailed / summary / by_staff / by_product / by_month).
`SalesReportExporter` only writes that result to a formatted `.xlsx` workbook
(Summary / Detailed / Staff / Products / Monthly sheets).
`SalesReportService` only calls these four components in order via
`generate(input_path, output_path)`; it contains no business logic of its
own. `gui.main_window.MainWindow` calls only `SalesReportService` — it never
imports `SalesDataReader`, `SalesDataValidator`, `SalesAnalyzer`, or
`SalesReportExporter` directly, and contains no business logic itself.
