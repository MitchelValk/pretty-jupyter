"""
Access to files shipped inside the package (templates, config, quickstart notebook).

Replaces ``pkg_resources.resource_filename``, which is deprecated and has been removed from
recent setuptools releases. nbconvert needs real directories on disk for its template paths,
so we resolve everything relative to the installed package directory.
"""

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent


def resource_path(*parts: str) -> str:
    """
    Returns the absolute filesystem path to a resource inside the ``pretty_jupyter`` package.

    >>> resource_path("templates")  # doctest: +SKIP
    '/.../site-packages/pretty_jupyter/templates'
    """
    return str(PACKAGE_DIR.joinpath(*parts))
