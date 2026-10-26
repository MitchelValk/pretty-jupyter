"""
itables in offline mode replaces the global `$` with its own jQuery. Pretty Jupyter must keep
working (TOC, sections) regardless of when that happens. Including plotly.js changes the timing
and used to reliably break the TOC.
"""
import subprocess
import sys
import time
from pathlib import Path

import pytest
from selenium.webdriver.common.by import By

pytest.importorskip("itables")


@pytest.fixture
def input_path(fixture_dir):
    return str(Path(fixture_dir, "itables.ipynb").resolve().as_posix())


def test_itables_offline(templates_path, input_path, out_path, page_url, driver):
    subprocess.run(
        [
            sys.executable,
            "-m",
            "jupyter",
            "nbconvert",
            "--to",
            "html",
            "--template",
            "pj",
            input_path,
            f"--TemplateExporter.extra_template_basedirs={templates_path}",
            "--execute",
            f"--output-dir={Path(out_path).parent}",
        ],
        check=True,
    )
    driver.get(page_url)
    time.sleep(1)

    toc_items = driver.find_elements(By.XPATH, "//div[@id='TOC']//li")
    assert len(toc_items) == 2, "TOC should contain both sections"

    tables = driver.find_elements(By.XPATH, "//div[contains(@class, 'dt-container')]")
    assert len(tables) == 2, "both interactive tables should be initialized"
