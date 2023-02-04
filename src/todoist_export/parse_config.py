"""Parse the config file.

:author: Shay Hill
:created: 2023-02-03
"""

import configparser
from pathlib import Path
from typing import Any, Callable, Literal

Filter = Callable[[str], bool]

CONFIG_FILE = Path("todoist_export.ini")

CONFIG_TEMPLATE = """
# Enter comma-separated lists of sections and projects to include or exclude. By
# default, every section and project will be included.
#
# -- If include_sections is blank, all sections will be included. If even one section
# is listed, then include_sections becomes a whitelist and only the listed sections
# will be included. The same rule applies for include_projects.
#
# -- Exclude trumps include, so if a section or project is both included and
# excluded, it will be excluded. There really isn't a good reason to have a whitelist
# and a blacklist. Just use whatever is easier for you.
#
# -- Any task without a section will be put in "no section" (all lowercase). See
# example for how to exclude.
#
# -- Entries here do not need quotes. Blank spaces in section or project names are
# fine.  Everything is case sensitive.
#
# example:
# include_sections = Active, Postponed, Delegated, Put on Hold
# exclude_sections = no section, Personal, Long Section Name With Multiple Spaces

[todoist.filter]
include_sections =
include_projects =
exclude_sections =
exclude_projects =
"""


def create_config_file():
    """Create a config file template if one doesn't exist."""
    if CONFIG_FILE.exists() and input().lower() != "y":
        return
    _ = CONFIG_FILE.write_text(CONFIG_TEMPLATE[1:])


class Everything:
    """A class that contains everything."""

    def __contains__(self, _: Any) -> Literal[True]:
        """Always returns True.

        :param _: Anything.
        :return: True.

        This is used to make a "whitelist" of everything.
        """
        return True


def _read_config() -> configparser.ConfigParser:
    """Read the config file and return a ConfigParser object.

    :return: A ConfigParser object with the config file loaded.
    """
    config = configparser.ConfigParser()
    config["todoist.filter"] = {
        "include_sections": "",
        "include_projects": "",
        "exclude_sections": "",
        "exclude_projects": "",
    }
    _ = config.read("todoist_export.ini")
    return config


def _split(config_value: str) -> set[str]:
    """Split a comma-separated string into a set of strings.

    :param config_value: The comma-separated string to split.
    :return: A set of (stripped) strings.
    """
    return {y.strip() for y in config_value.split(",") if y.strip()}


def get_user_defined_filters() -> tuple[Filter, Filter]:
    """Create filters from the config file (or defaults).

    :return: A tuple of (section_include_filter, project_include_filter).
    """
    config = _read_config()
    include_sections = _split(config["todoist.filter"]["include_sections"])
    include_projects = _split(config["todoist.filter"]["include_projects"])
    exclude_sections = _split(config["todoist.filter"]["exclude_sections"])
    exclude_projects = _split(config["todoist.filter"]["exclude_projects"])

    everything = Everything()

    def do_include_section(section: str) -> bool:
        """Return True if the section should be included in the export.

        :param section: The section to check.
        :return: True if the section should be included in the export.
        """
        if section in (include_sections or everything):
            return section not in exclude_sections
        return False

    def do_include_project(project: str) -> bool:
        """Return True if the project should be included in the export.

        :param project: The project to check.
        :return: True if the project should be included in the export.
        """
        if project in (include_projects or everything):
            return project not in exclude_projects
        return False

    return do_include_section, do_include_project
