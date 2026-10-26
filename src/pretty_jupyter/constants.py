from pretty_jupyter._resources import resource_path

MARKDOWN_TOKEN_REGEX = r"\s*\[.+\]:\s*(?:(?:<>)|#)\s*\(-\.-\s+(.*)\)"
"""
Regex to match markdown tokens. The tokens are special sequences in markdown that invoke special behaviour, e.g. tabsets. Example of some tokens:

```markdown
[//]: <> (-.- token1 token2 token3)
[//]: # (-.- token1 token2 token3)
```
"""


HTML_TOKEN_REGEX = r"<span class='pj-token' style='display: none;'>.*<\/span>"
"""
Regex to match html tokens.
"""

HTML_TOKEN_FORMAT = "<span class='pj-token' style='display: none;'>{tokens}</span>"
"""
What markdown tokens get translated to.
"""

TOKEN_SEP = "|O_O|"
"""Separator for multiple tokens"""

CODE_METADATA_TOKEN_REGEX = r"^\s*#\s+-\.-\|m\s+(.*)$"
"""
Regex to match markdown metadata tokens.

```python
# -.-|m { "input": false, "output": true }
```
"""

MARKDOWN_METADATA_TOKEN_REGEX = r"^\s*\[.+\]:\s*(?:(?:<>)|#)\s*\(-\.-\|m\s+(.*)\)\s*$"
"""
Regex to match markdown metadata tokens.

```markdown
[//]: # (-.-|m { "input": true, "output": false })
[//]: <> (-.-|m { "input": true, "output": false })
```
"""

CONFIG_DIR = resource_path("config")

AVAILABLE_THEMES = [
    "bootstrap",
    "cerulean",
    "cosmo",
    "cyborg",
    "darkly",
    "flatly",
    "journal",
    "lumen",
    "paper",
    "readable",
    "sandstone",
    "simplex",
    "slate",
    "spacelab",
    "superhero",
    "united",
    "yeti",
]
"""
List of all available local themes that can be specified in the `theme` html metadata.
"""

DARK_THEMES = ["cyborg", "darkly", "slate", "superhero"]
"""
Local themes with a dark background. Used to tell notebook outputs (e.g. itables) whether the page
is light or dark, instead of them guessing from the operating system's dark mode setting.
"""

CDN_ASSETS = {
    "static/libs/jquery.min.js": "https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js",
    "static/libs/bootstrap.min.js": "https://cdn.jsdelivr.net/npm/bootstrap@3.3.5/dist/js/bootstrap.min.js",
    "static/libs/plotly.min.js": "https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.13.3/plotly.min.js",
}
"""
Bundled libraries that can be loaded from a CDN when ``output.html.self_contained`` is false.
Only files that are byte-identical to the published npm packages are listed, so the subresource
integrity hash computed from the bundled copy also matches the CDN copy. Everything else
(themes, tocify, pj.js, ...) is always inlined.
"""

PLOTLY_MIMETYPE = "application/vnd.plotly.v1+json"

DEPRECATED_METADATA_MSG_FORMAT = "Specifying attributes '{attributes}' in this position to notebook metadata is deprecated since {version}. Please consider reading changes in this version.\n"
METADATA_ERROR_FORMAT = "An error occured when validating cell metadata. Error attributes in the metadata were the following:\n{error}"
