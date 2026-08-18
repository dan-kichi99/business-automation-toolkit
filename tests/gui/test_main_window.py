import tkinter as tk
from pathlib import Path

import pytest

from core.exceptions import ValidationError
from gui.main_window import STATUS_READY, STATUS_SUCCESS, MainWindow


class FakeService:
    def __init__(self, result=None, exception=None):
        self.result = result
        self.exception = exception
        self.calls: list[tuple] = []

    def generate(self, input_path, output_path):
        self.calls.append((input_path, output_path))
        if self.exception is not None:
            raise self.exception
        return self.result


@pytest.fixture(scope="session")
def tk_root():
    try:
        session_root = tk.Tk()
        session_root.withdraw()
    except tk.TclError as exc:
        pytest.skip(f"Tkinter display not available: {exc}")
    yield session_root
    session_root.destroy()


@pytest.fixture
def root(tk_root):
    window = tk.Toplevel(tk_root)
    window.withdraw()
    yield window
    window.destroy()


def make_window(root, service=None) -> MainWindow:
    return MainWindow(root, service=service or FakeService())


# ---- Initial state ----


def test_initial_state_has_no_paths(root):
    window = make_window(root)

    assert window.input_path is None
    assert window.output_path is None


def test_initial_generate_button_is_disabled(root):
    window = make_window(root)

    assert str(window.generate_button["state"]) == "disabled"


# ---- Selecting files ----


def test_selecting_only_input_keeps_generate_disabled(root, monkeypatch):
    window = make_window(root)
    monkeypatch.setattr(
        "gui.main_window.filedialog.askopenfilename", lambda **kwargs: "sales.csv"
    )

    window._browse_input()

    assert window.input_path == Path("sales.csv")
    assert str(window.generate_button["state"]) == "disabled"


def test_selecting_input_and_output_enables_generate(root, monkeypatch, tmp_path):
    window = make_window(root)
    input_path = tmp_path / "sales.csv"
    output_path = tmp_path / "sales_report.xlsx"
    monkeypatch.setattr(
        "gui.main_window.filedialog.askopenfilename", lambda **kwargs: str(input_path)
    )
    monkeypatch.setattr(
        "gui.main_window.filedialog.asksaveasfilename", lambda **kwargs: str(output_path)
    )

    window._browse_input()
    window._browse_output()

    assert window.input_path == input_path
    assert window.output_path == output_path
    assert str(window.generate_button["state"]) == "normal"


def test_cancelling_file_dialog_does_not_set_path(root, monkeypatch):
    window = make_window(root)
    monkeypatch.setattr("gui.main_window.filedialog.askopenfilename", lambda **kwargs: "")

    window._browse_input()

    assert window.input_path is None


# ---- Generate: service integration ----


def test_generate_calls_service_with_selected_paths(root, tmp_path):
    service = FakeService(result=tmp_path / "sales_report.xlsx")
    window = make_window(root, service=service)
    window.input_path = tmp_path / "sales.csv"
    window.output_path = tmp_path / "sales_report.xlsx"

    window._on_generate()

    assert service.calls == [(window.input_path, window.output_path)]


def test_generate_success_updates_status_and_shows_info(root, monkeypatch, tmp_path):
    report_path = tmp_path / "sales_report.xlsx"
    service = FakeService(result=report_path)
    window = make_window(root, service=service)
    window.input_path = tmp_path / "sales.csv"
    window.output_path = report_path

    shown = {}
    monkeypatch.setattr(
        "gui.main_window.messagebox.showinfo",
        lambda title, message: shown.update(title=title, message=message),
    )

    window._on_generate()

    assert window.status_var.get() == STATUS_SUCCESS
    assert str(report_path) in shown["message"]


def test_generate_business_error_shows_error_and_resets_status(root, monkeypatch, tmp_path):
    service = FakeService(exception=ValidationError("Missing required columns: price"))
    window = make_window(root, service=service)
    window.input_path = tmp_path / "sales.csv"
    window.output_path = tmp_path / "sales_report.xlsx"

    shown = {}
    monkeypatch.setattr(
        "gui.main_window.messagebox.showerror",
        lambda title, message: shown.update(title=title, message=message),
    )

    window._on_generate()

    assert window.status_var.get() == STATUS_READY
    assert "Missing required columns" in shown["message"]


def test_generate_unexpected_error_shows_generic_message(root, monkeypatch, tmp_path):
    service = FakeService(exception=RuntimeError("boom"))
    window = make_window(root, service=service)
    window.input_path = tmp_path / "sales.csv"
    window.output_path = tmp_path / "sales_report.xlsx"

    shown = {}
    monkeypatch.setattr(
        "gui.main_window.messagebox.showerror",
        lambda title, message: shown.update(title=title, message=message),
    )

    window._on_generate()

    assert window.status_var.get() == STATUS_READY
    assert "unexpected error" in shown["message"].lower()
    assert "boom" not in shown["message"]


# ---- Button re-enable ----


def test_generate_button_reenabled_after_success(root, monkeypatch, tmp_path):
    service = FakeService(result=tmp_path / "sales_report.xlsx")
    window = make_window(root, service=service)
    window.input_path = tmp_path / "sales.csv"
    window.output_path = tmp_path / "sales_report.xlsx"
    monkeypatch.setattr("gui.main_window.messagebox.showinfo", lambda title, message: None)

    window._on_generate()

    assert str(window.generate_button["state"]) == "normal"


def test_generate_button_reenabled_after_failure(root, monkeypatch, tmp_path):
    service = FakeService(exception=ValidationError("bad data"))
    window = make_window(root, service=service)
    window.input_path = tmp_path / "sales.csv"
    window.output_path = tmp_path / "sales_report.xlsx"
    monkeypatch.setattr("gui.main_window.messagebox.showerror", lambda title, message: None)

    window._on_generate()

    assert str(window.generate_button["state"]) == "normal"
