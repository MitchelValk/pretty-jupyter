"""
Packaging and robustness checks that don't need a browser.
"""

import configparser
from pathlib import Path

import nbformat
import pytest
from nbconvert.exporters import HTMLExporter
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook, new_output, new_raw_cell
from traitlets.config import Config

from pretty_jupyter._resources import resource_path
from pretty_jupyter.constants import CDN_ASSETS
from pretty_jupyter.preprocessors._metadata_preprocessor import get_cdn_assets, notebook_uses_plotly

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = Path(resource_path("templates"))
STATIC_DIR = TEMPLATES_DIR / "pj" / "static"


def _export_html(nb):
    config = Config()
    config.TemplateExporter.template_name = "pj"
    config.TemplateExporter.extra_template_basedirs = [str(TEMPLATES_DIR)]
    html, _ = HTMLExporter(config=config).from_notebook_node(nb)
    return html


def test_resources_exist():
    assert (TEMPLATES_DIR / "pj" / "index.html.j2").is_file()
    assert Path(resource_path("config", "metadata", "nb_defaults.yaml")).is_file()
    assert Path(resource_path("quickstart", "empty.ipynb")).is_file()


@pytest.mark.parametrize("path", sorted(p.name for p in (STATIC_DIR / "libs").glob("*.js")))
def test_bundled_js_is_safe_to_inline(path):
    # inline <script> blocks end at the first "</script" and "<!--" changes how they are parsed
    text = (STATIC_DIR / "libs" / path).read_text(encoding="utf-8").lower()
    assert "</script" not in text
    assert "<!--" not in text


def test_setup_cfg_lists_all_template_files():
    """data_files in setup.cfg must be kept in sync with the template folders by hand."""
    parser = configparser.ConfigParser()
    parser.read(REPO_ROOT / "setup.cfg")
    listed = {
        Path(line.strip()).as_posix()
        for value in parser["options.data_files"].values()
        for line in value.strip().splitlines()
    }
    on_disk = {
        p.relative_to(REPO_ROOT).as_posix()
        for template in ("pj", "pj-legacy", "pj-pdf")
        for p in (TEMPLATES_DIR / template).rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    }
    assert on_disk - listed == set(), "template files missing from setup.cfg [options.data_files]"
    assert listed - on_disk == set(), "setup.cfg lists template files that don't exist"


def test_cdn_assets_have_integrity():
    assets = get_cdn_assets()
    assert set(assets) == set(CDN_ASSETS)
    for asset in assets.values():
        assert asset["url"].startswith("https://")
        assert asset["integrity"].startswith("sha384-")


def test_empty_notebook_exports():
    html = _export_html(new_notebook())
    assert "<title>Untitled</title>" in html


def test_empty_raw_metadata_cell_exports():
    nb = new_notebook(cells=[new_raw_cell(""), new_markdown_cell("# Hello")])
    html = _export_html(nb)
    assert "<title>Untitled</title>" in html


def test_non_mapping_raw_metadata_cell_has_clear_error():
    nb = new_notebook(cells=[new_raw_cell("just some text")])
    with pytest.raises(ValueError, match="YAML mapping"):
        _export_html(nb)


def _nb_with_output(data):
    cell = new_code_cell("x", outputs=[new_output("display_data", data=data)])
    return nbformat.from_dict(new_notebook(cells=[cell]))


def test_notebook_uses_plotly():
    assert notebook_uses_plotly(_nb_with_output({"application/vnd.plotly.v1+json": {}}))
    assert notebook_uses_plotly(_nb_with_output({"text/html": "<script>Plotly.newPlot()</script>"}))
    assert notebook_uses_plotly(_nb_with_output({"text/markdown": ["<div>", "Plotly.newPlot"]}))
    assert not notebook_uses_plotly(_nb_with_output({"text/plain": "<plotly Figure>"}))
    assert not notebook_uses_plotly(_nb_with_output({"text/html": "<b>hi</b>"}))
    assert not notebook_uses_plotly(new_notebook(cells=[new_markdown_cell("We use plotly.")]))


@pytest.mark.parametrize("theme,light", [("paper", "true"), ("darkly", "false")])
def test_body_declares_light_or_dark_theme(theme, light):
    # outputs like itables follow data-jp-theme-light instead of the OS dark mode setting
    nb = new_notebook(cells=[new_raw_cell(f"output:\n  html:\n    theme: {theme}\n")])
    assert f'<body data-jp-theme-light="{light}">' in _export_html(nb)


def test_body_custom_theme_url_has_no_theme_flag():
    nb = new_notebook(
        cells=[new_raw_cell("output:\n  html:\n    theme: https://example.com/t.css\n")]
    )
    html = _export_html(nb)
    assert "<body>" in html and "data-jp-theme-light" not in html


def test_plotly_figure_output_becomes_interactive_html():
    figure = {"data": [{"type": "scatter", "y": [1, 3, 2], "name": "</script><!--"}], "layout": {}}
    svg = "<svg><text>static</text></svg>"
    nb = _nb_with_output({"application/vnd.plotly.v1+json": figure, "image/svg+xml": svg})
    html = _export_html(nb)
    assert "Plotly.newPlot" in html
    assert "<text>static</text>" not in html, "html should win over the static svg"
    # figure JSON must not be able to break out of the <script> block
    assert "</script><!--" not in html


def test_existing_plotly_html_is_kept():
    custom = '<div id="mine"></div><script>Plotly.newPlot("mine", [])</script>'
    nb = _nb_with_output({"application/vnd.plotly.v1+json": {"data": []}, "text/html": custom})
    html = _export_html(nb)
    assert custom in html
    assert "pj-plotly-" not in html


def test_plotlyjs_falls_back_to_bundled_copy(monkeypatch):
    import importlib.util

    from pretty_jupyter import _plotly

    monkeypatch.setattr(importlib.util, "find_spec", lambda name: None)
    path, version = _plotly.find_plotlyjs()
    assert path == _plotly.BUNDLED_PLOTLYJS
    assert version is not None


def test_plotlyjs_unsafe_source_is_base64_encoded(monkeypatch, tmp_path):
    from pretty_jupyter import _plotly

    js = tmp_path / "plotly.min.js"
    js.write_text("/* plotly.js v9.9.9 */ var s = '</script>';", encoding="utf-8")
    monkeypatch.setattr(_plotly, "find_plotlyjs", lambda: (js, "9.9.9"))
    tag = _plotly.plotlyjs_script_tag()
    assert tag.startswith('<script src="data:text/javascript;base64,')
    assert "</script>'" not in tag
