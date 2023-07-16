"""Pull tasks from todoist and create a table.

Put tasks into a table with the following columns:
[
    (section name, project name, task content),
    (section name, project name, task content),
    (section name, project name, task content),
]

Sort these so identical section names are adjacent. Send to write_wip.

:author: Shay Hill
:created: 2023-02-03
"""

import datetime
import sys
import os

from todoist_tree.headers import new_headers
from todoist_tree.read_changes import Project, Section, Task, Todoist, read_changes

from todoist_export.parse_config import create_config_file, get_user_defined_filters
from todoist_export.write_export import write_wip

from contextlib import suppress

HIDDEN_COMMAND = "config"

def _get_api_key() -> str:
    """Look for an environment variable for a Todoist API key. If that fails, ask user.
    """
    with suppress(KeyError):
        return os.environ["TODOIST_API_KEY"]
    return input("Enter your Todoist API token: ")

def _map_section_id_to_name(sections: list[Section]) -> dict[str, str]:
    """Create a dictionary of section id to section name.

    :param sections: list of sections
    :return: dictionary of section id to section name
    """
    return {section.id: section.name for section in sections}


def _map_project_id_to_name(projects: list[Project]) -> dict[str, str]:
    """Create a dictionary of project id to project name.

    :param projects: list of projects
    :return: dictionary of project id to project name
    """
    return {project.id: project.name for project in projects}


def _get_timestamp() -> str:
    """Create a timestamp for the export file name.

    :return: timestamp
    """
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d_%H-%M-%S")


def _create_table_line(
    task: Task, id2section: dict[str, str], id2project: dict[str, str]
) -> tuple[str, str, str]:
    """Create a line for the table.

    :param task: task
    :param sections: dictionary of section id to section name
    :param projects: dictionary of project id to project name
    :return: tuple of section name, project name, task content

    You should never have a "no project" in the table, but it's possible according to
    the API. Will handle it gracefully just in case.
    """
    section_name = id2section.get(str(task.section_id), "no section")
    project_name = id2project.get(str(task.project_id), "no project")
    return (section_name, project_name, task.content)


def _get_api_token_or_command() -> str:
    """Ask user for Todoist API token.

    :return: Todoist API token
    :effect: a hidden command, `config`, will create a template ini file if entered
        at the API-token prompt.
    """
    api_token: str | None = None
    while not api_token:
        api_token = _get_api_key()
        # TODO: remove the HIDDEN_COMMAND or find some way to enter it.
        if api_token == HIDDEN_COMMAND:
            create_config_file()
            api_token = None
    return api_token


def _read_todoist() -> Todoist | None:
    """Get an api_token from the user and read the Todoist data.

    :return: Todoist api result wrapped in a Todoist object or None if failed.
    """
    api_token = _get_api_token_or_command()
    headers = new_headers(api_token)
    _ = sys.stdout.write("Reading Todoist data...\n")
    return read_changes(headers)

def _get_today() -> str:
    """Return today's date in YYYY-MM-DD format."""
    return datetime.date.today().strftime("%Y-%m-%d")

def _create_table(todoist: Todoist) -> list[tuple[str, str, str]]:
    """Create the table.

    :return: list of tuples of section name, project name, task content
    """
    filter_table = get_user_defined_filters()

    id2section = _map_section_id_to_name(todoist.sections)
    id2project = _map_project_id_to_name(todoist.projects)
    tasks = todoist.tasks
    today = [x for x in tasks if x.due and x.due['date'][:10] == _get_today()]
    table_lines = [_create_table_line(t, id2section, id2project) for t in today]
    return sorted(filter(filter_table, table_lines))

def _main():
    """Main function.

    :effect: write a docx file with the table of tasks
    """
    todoist = _read_todoist()
    if todoist is None:
        _ = sys.stdout.write("Failed to read Todoist data.\n")
        _ = input("press Enter to close...")
        return

    table_lines = _create_table(todoist)
    with open("temp", "w", encoding="utf-8") as f:
        for line in table_lines:
            tab = "\t"
            _ = f.write(f"{tab.join(line[-1:])}")
            _ = f.write("\n")
    filename = f"todoist_{_get_timestamp()}.docx"
    breakpoint()
    write_wip(filename, table_lines)
    _ = sys.stdout.write(f"{len(table_lines)} tasks exported to '{filename}'\n")
    _ = input("press Enter to close...")


if __name__ == "__main__":
    _main()
