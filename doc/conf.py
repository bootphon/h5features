"""Sphinx configuration."""

from datetime import UTC, datetime
from importlib.metadata import metadata

project = "h5features"
author = metadata(project)["Author-email"].split(" ")[0]
copyright = f"2020-{datetime.now(tz=UTC).year} {author}"  # noqa: A001
version = metadata(project)["Version"]
release = version

html_static_path = ["static"]
html_theme = "furo"
extensions = ["sphinx.ext.autodoc", "breathe", "enum_tools.autoenum"]
python_use_unqualified_type_names = True
autoclass_content = "init"
breathe_projects = {project: "./xml"}
breathe_default_project = project
breathe_default_members = ("members", "undoc-members")
