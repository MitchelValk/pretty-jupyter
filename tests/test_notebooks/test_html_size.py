"""
Tests for the HTML output size options: include_plotlyjs (incl. "auto") and self_contained.
"""

import os
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest
from selenium.webdriver.common.by import By

from pretty_jupyter.constants import CDN_ASSETS

PLOTLY_BUNDLE_MARKER = "plotly.js v2.13.3"


def _convert(input_path, out_dir, templates_path, pj_metadata=None):
    cmd = [
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
        f"--output-dir={out_dir}",
    ]
    if pj_metadata is not None:
        cmd.append(f"--HtmlNbMetadataPreprocessor.pj_metadata={pj_metadata}")
    subprocess.run(cmd, check=True)


@pytest.fixture
def input_path(fixture_dir):
    return str(Path(fixture_dir, "plotly.ipynb").resolve().as_posix())


def test_plotly_auto_included_and_renders(templates_path, input_path, out_path, page_url, driver):
    _convert(input_path, os.path.dirname(out_path), templates_path)

    html = Path(out_path).read_text(encoding="utf-8")
    assert PLOTLY_BUNDLE_MARKER in html, "plotly.js should be inlined when the notebook uses plotly"
    # libraries are inlined as text, not as base64 data URIs
    assert "data:text/javascript;base64" not in html

    driver.get(page_url)
    time.sleep(1)
    plots = driver.find_elements(
        By.XPATH, "//div[contains(@class, 'js-plotly-plot')]//*[name()='svg']"
    )
    assert len(plots) > 0, "plotly figure did not render"


def test_plotly_auto_excluded(templates_path, fixture_dir, tmpdir):
    # toc.ipynb has no plotly output => plotly.js should be left out
    input_path = str(Path(fixture_dir, "toc.ipynb").resolve().as_posix())
    _convert(input_path, str(tmpdir), templates_path)
    html = Path(tmpdir, "toc.html").read_text(encoding="utf-8")
    assert PLOTLY_BUNDLE_MARKER not in html


def test_plotly_forced(templates_path, fixture_dir, tmpdir):
    input_path = str(Path(fixture_dir, "toc.ipynb").resolve().as_posix())
    _convert(input_path, str(tmpdir), templates_path, "{output: {html: {include_plotlyjs: true}}}")
    html = Path(tmpdir, "toc.html").read_text(encoding="utf-8")
    assert PLOTLY_BUNDLE_MARKER in html


def test_plotly_disabled(templates_path, input_path, out_path):
    _convert(
        input_path,
        os.path.dirname(out_path),
        templates_path,
        "{output: {html: {include_plotlyjs: false}}}",
    )
    html = Path(out_path).read_text(encoding="utf-8")
    assert PLOTLY_BUNDLE_MARKER not in html


def test_not_self_contained(templates_path, input_path, out_path):
    _convert(
        input_path,
        os.path.dirname(out_path),
        templates_path,
        "{output: {html: {self_contained: false}}}",
    )
    html = Path(out_path).read_text(encoding="utf-8")

    assert PLOTLY_BUNDLE_MARKER not in html
    # attribute order differs between nbconvert versions (nbconvert 7 re-serializes the page)
    script_tags = re.findall(r"<script\b[^>]*>", html)
    for url in CDN_ASSETS.values():
        tags = [t for t in script_tags if f'src="{url}"' in t]
        assert len(tags) == 1, f"{url} should be loaded from the CDN"
        assert re.search(r'integrity="sha384-[A-Za-z0-9+/=]+"', tags[0])
        assert 'crossorigin="anonymous"' in tags[0]
