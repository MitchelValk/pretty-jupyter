Changelog
============================


2.0.0
-----------

- Added other themes and required.js directly to the report.
- Fixed an issue with weird characters ruining tabset and toc (characters like parentheses, braces, square brackets, #, ", ', etc)
- Fixed an issue where empty jinja markdown cell would lead to an error when running pretty jupyter
- Added ``code_tools`` to html output options to provide an option to enable / disable code tools. Default value is false.
- Implemented cell and notebook-level metadata.
- Changed design, added the old one to pj-legacy template.
- Added experimental direct pdf output with pj-pdf template.
- Updated documentation, added section for metadata, modified existing bits.
- Allowed to specify classes for any Markdown / HTML element.
- Changed internal representation of tokens.
- Changed tokens convention (tabset -> .tabset). It is still backwards compatible though.
- Implemented script that creates basic ipynb document with Pretty Jupyter basic elements (title,...).
- Switched from setup.py to setup.cfg and pyproject.toml.
- Added detailed selenium tests for notebooks generating.

**Breaking Changes**

- Changed tokens output representation: Solution is to re-execute the notebook with the new version of Pretty Jupyter.
- Implemented notebook-level metadata: Previous title, theme etc. needs to be moved to the new places. Check out :doc:`metadata` page.
- Change of html template structure: This is problem only if you have a custom template. In such a case, check out :doc:`custom_template`. Changing your inheriting template should require minimum changes.

2.0.1
~~~~~~~
- Fixed ``pretty-jupyter quickstart``
- Improved documentation

2.0.2
~~~~~~~
- Improved styles for small screens.

2.1.0
~~~~~~~
- Removed the dependency on ``pkg_resources`` (removed from recent setuptools); package files are located relative to the package instead.
- Supports nbconvert 7 in addition to nbconvert 6. Supported Python versions are now 3.8 - 3.13.
- Much smaller html output: bundled libraries are inlined as text instead of base64 data URIs, only the jQuery UI widget factory (needed by the TOC) is included instead of all of jQuery UI, and plotly.js is only included when the notebook uses it (``include_plotlyjs: auto``, the new default). A typical report goes from ~5.7 MB to ~0.35 MB.
- Added ``output.html.self_contained`` option. When false, jQuery, Bootstrap and plotly.js are loaded from a CDN with subresource integrity hashes.
- Notebooks without cells and empty raw metadata cells no longer crash the export; a non-YAML first raw cell gives a clear error.
- ``pretty-jupyter quickstart`` copies the notebook byte for byte (fixes encoding issues on Windows).
