from pathlib import Path

from core.paths import OUTPUT_DIR, PROJECT_ROOT, SAMPLES_DIR


def test_project_root_is_path():
    assert isinstance(PROJECT_ROOT, Path)


def test_output_dir_is_under_project_root():
    assert OUTPUT_DIR.parent == PROJECT_ROOT


def test_samples_dir_is_under_project_root():
    assert SAMPLES_DIR.parent == PROJECT_ROOT
