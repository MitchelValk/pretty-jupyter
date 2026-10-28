"""
Plotly support: which plotly.js to embed and how to turn plotly figure outputs into interactive HTML.
"""

import base64
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Optional, Tuple

from pretty_jupyter._resources import resource_path

BUNDLED_PLOTLYJS = Path(resource_path("templates", "pj", "static", "libs", "plotly.min.js"))
"""Fallback plotly.js shipped with pretty-jupyter, used when the plotly package isn't installed."""

PLOTLYJS_CDN_FORMAT = "https://cdn.jsdelivr.net/npm/plotly.js-dist-min@{version}/plotly.min.js"
"""
CDN location for ``self_contained: false``. The plotly Python package ships the unmodified
``plotly.js-dist-min`` build, so the integrity hash computed from the local file matches it.
"""

_VERSION_REGEX = re.compile(rb"plotly\.js v(\d+\.\d+\.\d+\S*)")


def find_plotlyjs() -> Tuple[Path, Optional[str]]:
    """
    Returns ``(path, version)`` of the plotly.js to embed.

    Prefers the plotly.js bundled with the installed ``plotly`` Python package, because figures are
    serialized for exactly that version (e.g. plotly 6+ encodes numpy arrays in a format older
    plotly.js can't read). Falls back to the copy shipped with pretty-jupyter.
    """
    path = BUNDLED_PLOTLYJS
    try:
        spec = importlib.util.find_spec("plotly")
    except (ImportError, ValueError):
        spec = None
    if spec is not None and spec.origin:
        candidate = Path(spec.origin).parent / "package_data" / "plotly.min.js"
        if candidate.is_file():
            path = candidate

    with open(path, "rb") as file:
        match = _VERSION_REGEX.search(file.read(1000))
    return path, match.group(1).decode("ascii") if match else None


def is_safe_to_inline(js: str) -> bool:
    """
    Whether ``js`` can be put between ``<script>`` and ``</script>`` as-is. The HTML parser ends the
    block at the first ``</script`` and ``<!--`` followed by ``<script`` changes how it is parsed.
    """
    lowered = js.lower()
    return "</script" not in lowered and not ("<!--" in lowered and "<script" in lowered)


def plotlyjs_script_tag(self_contained: bool = True) -> str:
    """
    Returns the ``<script>`` tag that loads plotly.js: inline text when possible, a base64 data URI
    if the source can't be inlined safely, or a CDN link with an integrity hash when
    ``self_contained`` is false (and the version is known).
    """
    path, version = find_plotlyjs()
    data = path.read_bytes()

    if not self_contained and version is not None:
        integrity = "sha384-" + base64.b64encode(hashlib.sha384(data).digest()).decode("ascii")
        url = PLOTLYJS_CDN_FORMAT.format(version=version)
        return f'<script src="{url}" integrity="{integrity}" crossorigin="anonymous"></script>'

    js = data.decode("utf-8")
    if is_safe_to_inline(js):
        return f"<script>\n{js}\n</script>"
    encoded = base64.b64encode(data).decode("ascii")
    return f'<script src="data:text/javascript;base64,{encoded}"></script>'


def figure_to_html(figure: dict, div_id: str) -> str:
    """
    Renders a plotly figure (the ``application/vnd.plotly.v1+json`` output) as an interactive
    ``<div>`` + ``<script>``. Requires plotly.js to be loaded on the page.
    """
    layout = figure.get("layout") or {}
    height = layout.get("height")
    width = layout.get("width")
    height_css = f"{height}px" if isinstance(height, (int, float)) else "525px"
    width_css = f"{width}px" if isinstance(width, (int, float)) else "100%"

    payload = {
        "data": figure.get("data") or [],
        "layout": layout,
        "frames": figure.get("frames") or [],
        "config": {"responsive": True, **(figure.get("config") or {})},
    }
    # keep the JSON from closing the <script> block or opening an HTML comment
    fig_json = json.dumps(payload).replace("</", "<\\/").replace("<!--", "<\\u0021--")

    return (
        f'<div id="{div_id}" class="plotly-graph-div" '
        f'style="height:{height_css}; width:{width_css};"></div>\n'
        '<script type="text/javascript">\n'
        "(function () {\n"
        f"  var fig = {fig_json};\n"
        f'  var gd = document.getElementById("{div_id}");\n'
        "  if (!window.Plotly) {\n"
        '    gd.textContent = "plotly.js is not loaded; set include_plotlyjs to true or auto.";\n'
        "    return;\n"
        "  }\n"
        "  Plotly.newPlot(gd, fig.data, fig.layout, fig.config).then(function () {\n"
        "    if (fig.frames.length > 0) { return Plotly.addFrames(gd, fig.frames); }\n"
        "  });\n"
        "})();\n"
        "</script>"
    )
