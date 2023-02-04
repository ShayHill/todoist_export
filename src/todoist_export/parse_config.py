"""Parse the config file.

:author: Shay Hill
:created: 2023-02-03
"""

import configparser
import sys
from pathlib import Path
from typing import Callable

CONFIG_FILE = Path("todoist_export.ini")

CONFIG_TEMPLATE = """
# Enter comma-separated lists of sections and projects to include or exclude. By
# default, every section and project will be included.
#
# -- If section_whitelist is blank, all sections will be included. If even one section
# is listed, then section_whitelist becomes a whitelist and only the listed sections
# will be included. The same rule applies for project_whitelist.
#
# -- Blacklist trumps whitelist, so if a section or project is both whitelisted and
# blacklisted, it will be excluded. There really isn't a good reason to have both a
# whitelist and a blacklist. Just use whatever is easier for you.
#
# -- Any task without a section will be put in "no section" (all lowercase). See
# example for how to exclude.
#
# -- Entries here do not need quotes. Blank spaces in section or project names are
# fine. Everything is case sensitive.
#
# -- example entries:
# section_whitelist = Active, Postponed, Delegated, Put on Hold
# section_blacklist = no section, Personal, Long Section Name With Multiple Spaces

[todoist.filter]
section_whitelist =
project_whitelist =
section_blacklist =
project_blacklist =
"""


def create_config_file():
    """Create a config file template if one doesn't exist."""
    if CONFIG_FILE.exists():
        do_overwrite = input(f"Config file '{CONFIG_FILE}' exists. Overwrite? (y/N) ")
        if do_overwrite.lower() != "y":
            return
    _ = CONFIG_FILE.write_text(CONFIG_TEMPLATE[1:])
    _ = sys.stdout.write(f"Config file '{CONFIG_FILE}' created.\n")


def _read_config() -> configparser.ConfigParser:
    """Read the config file and return a ConfigParser object.

    :return: A ConfigParser object with the config file loaded.
    """
    config = configparser.ConfigParser()
    config["todoist.filter"] = {
        "section_whitelist": "",
        "project_whitelist": "",
        "section_blacklist": "",
        "project_blacklist": "",
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
    section_whitelist = _split(config["todoist.filter"]["section_whitelist"])
    project_whitelist = _split(config["todoist.filter"]["project_whitelist"])
    section_blacklist = _split(config["todoist.filter"]["section_blacklist"])
    project_blacklist = _split(config["todoist.filter"]["project_blacklist"])

    def filter_table(table_line: tuple[str, str, str]) -> bool:
        """Return True if the task should be included in the export.

        :param table_line: (section name, project name, task content) tuple.
        :return: True if the task should be included in the export.
        """
        section, project, _ = table_line
        if section in section_blacklist:
            return False
        if project in project_blacklist:
            return False
        if section_whitelist and section not in section_whitelist:
            return False
        if project_whitelist and project not in project_whitelist:
            return False
        return True

    return filter_table
