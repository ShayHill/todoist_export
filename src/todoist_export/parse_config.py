"""Parse the config file.

:author: Shay Hill
:created: 2023-02-03
"""

import configparser
from pathlib import Path
from typing import Callable

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
# fine. Everything is case sensitive.
#
# -- example entries:
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


def get_user_defined_filters() -> Callable[[tuple[str, str, str]], bool]:
    """Create filters from the config file (or defaults).

    :return: A tuple of (section_include_filter, project_include_filter).
    """
    config = _read_config()
    include_sections = _split(config["todoist.filter"]["include_sections"])
    include_projects = _split(config["todoist.filter"]["include_projects"])
    exclude_sections = _split(config["todoist.filter"]["exclude_sections"])
    exclude_projects = _split(config["todoist.filter"]["exclude_projects"])

    def filter_table(table_line: tuple[str, str, str]) -> bool:
        """Return True if the task should be included in the export.

        :param table_line: (section name, project name, task content) tuple.
        :return: True if the task should be included in the export.
        """
        section, project, _ = table_line
        if section in exclude_sections:
            return False
        if project in exclude_projects:
            return False
        if include_sections and section not in include_sections:
            return False
        if include_projects and project not in include_projects:
            return False
        return True

    return filter_table
