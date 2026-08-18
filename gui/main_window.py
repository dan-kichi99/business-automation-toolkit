import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from core.exceptions import BusinessAutomationError
from core.logger import get_logger
from modules.sales_report.service import SalesReportService

logger = get_logger(__name__)

INPUT_FILETYPES = [
    ("Sales Data", "*.csv *.xlsx"),
    ("CSV Files", "*.csv"),
    ("Excel Files", "*.xlsx"),
    ("All Files", "*.*"),
]
OUTPUT_FILETYPES = [("Excel Workbook", "*.xlsx")]
DEFAULT_OUTPUT_FILENAME = "sales_report.xlsx"

NOT_SELECTED = "Not selected"
STATUS_READY = "Ready"
STATUS_PROCESSING = "Processing..."
STATUS_SUCCESS = "Report generated successfully."


class MainWindow:
    def __init__(self, root: tk.Tk, service: SalesReportService | None = None) -> None:
        self.root = root
        self.service = service or SalesReportService()

        self.input_path: Path | None = None
        self.output_path: Path | None = None

        self.input_path_var = tk.StringVar(value=NOT_SELECTED)
        self.output_path_var = tk.StringVar(value=NOT_SELECTED)
        self.status_var = tk.StringVar(value=STATUS_READY)

        self._build_widgets()

    def _build_widgets(self) -> None:
        self.root.title("Business Automation Toolkit")
        self.root.geometry("600x300")

        ttk.Label(
            self.root, text="Business Automation Toolkit", font=("Arial", 16, "bold")
        ).pack(padx=20, pady=(20, 0))
        ttk.Label(self.root, text="Sales Report Generator").pack(padx=20, pady=(0, 15))

        input_frame = ttk.Frame(self.root)
        input_frame.pack(fill="x", padx=20, pady=5)
        ttk.Label(input_frame, text="Input File:", width=12).pack(side="left")
        ttk.Label(input_frame, textvariable=self.input_path_var, anchor="w").pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(input_frame, text="Browse", command=self._browse_input).pack(side="left")

        output_frame = ttk.Frame(self.root)
        output_frame.pack(fill="x", padx=20, pady=5)
        ttk.Label(output_frame, text="Output File:", width=12).pack(side="left")
        ttk.Label(output_frame, textvariable=self.output_path_var, anchor="w").pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(output_frame, text="Save As", command=self._browse_output).pack(side="left")

        self.generate_button = ttk.Button(
            self.root,
            text="Generate Report",
            command=self._on_generate,
            state="disabled",
        )
        self.generate_button.pack(pady=15)

        ttk.Label(self.root, textvariable=self.status_var).pack(pady=(0, 10))

    def _browse_input(self) -> None:
        selected = filedialog.askopenfilename(
            title="Select Sales Data File", filetypes=INPUT_FILETYPES
        )
        if not selected:
            return

        self.input_path = Path(selected)
        self.input_path_var.set(str(self.input_path))
        self._update_generate_button_state()

    def _browse_output(self) -> None:
        selected = filedialog.asksaveasfilename(
            title="Save Report As",
            defaultextension=".xlsx",
            filetypes=OUTPUT_FILETYPES,
            initialfile=DEFAULT_OUTPUT_FILENAME,
        )
        if not selected:
            return

        self.output_path = Path(selected)
        self.output_path_var.set(str(self.output_path))
        self._update_generate_button_state()

    def _update_generate_button_state(self) -> None:
        if self.input_path and self.output_path:
            self.generate_button.configure(state="normal")
        else:
            self.generate_button.configure(state="disabled")

    def _on_generate(self) -> None:
        if not (self.input_path and self.output_path):
            return

        self.status_var.set(STATUS_PROCESSING)
        self.generate_button.configure(state="disabled")
        self.root.update_idletasks()

        try:
            logger.info("Report generation started")
            report_path = self.service.generate(self.input_path, self.output_path)
        except BusinessAutomationError as exc:
            self.status_var.set(STATUS_READY)
            messagebox.showerror("Report Generation Failed", str(exc))
        except Exception:
            logger.exception("Unexpected error during report generation")
            self.status_var.set(STATUS_READY)
            messagebox.showerror(
                "Unexpected Error",
                "An unexpected error occurred.\nPlease try again.",
            )
        else:
            logger.info("Report generation completed")
            self.status_var.set(STATUS_SUCCESS)
            messagebox.showinfo("Success", f"Report generated successfully.\n\n{report_path}")
        finally:
            self._update_generate_button_state()


def launch() -> None:
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()
