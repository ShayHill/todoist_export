"""Pull tasks from todoist and create a table.

:author: Shay Hill
:created: 2023-02-03
"""


import datetime

from todoist_tree.headers import new_headers
from todoist_tree.read_changes import Project, Section, Task, read_changes

from todoist_export.parse_config import create_config_file, get_user_defined_filters
from todoist_export.write_export import write_wip

HIDDEN_COMMAND = "config"


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
    task: Task, sections: dict[str, str], projects: dict[str, str]
) -> tuple[str, str, str]:
    """Create a line for the table.

    :param task: task
    :param sections: dictionary of section id to section name
    :param projects: dictionary of project id to project name
    :return: tuple of section name, project name, task content

    You should never have a "no project" in the table, but it's possible according to
    the API. Will handle it gracefully just in case.
    """
    section_name = sections.get(str(task.section_id), "no section")
    project_name = projects.get(str(task.project_id), "no project")
    return (section_name, project_name, task.content)


def _get_api_token() -> str:
    """Ask user for Todoist API token.

    :return: Todoist API token
    :effect: a secret entry, `config`, will create a template ini file.
    """
    api_token: str | None = None
    while not api_token:
        api_token = input("Enter your Todoist API token: ")
        if api_token == HIDDEN_COMMAND:
            create_config_file()
            api_token = None
    return api_token


def _create_table():
    # ask user for api token
    api_token = _get_api_token()
    do_include_section, do_include_project = get_user_defined_filters()

    headers = new_headers(api_token)
    todoist = read_changes(headers)
    if todoist is None:
        return
    sections = _map_section_id_to_name(todoist.sections)
    projects = _map_project_id_to_name(todoist.projects)
    tasks = todoist.tasks
    table_lines = [_create_table_line(task, sections, projects) for task in tasks]
    table_lines = [x for x in table_lines if do_include_section(x[0])]
    table_lines = [x for x in table_lines if do_include_project(x[1])]
    table_lines.sort()

    timestamp = _get_timestamp()
    filename = f"todoist_{timestamp}.docx"
    write_wip(filename, table_lines)
    _ = input("press Enter to close...")


if __name__ == "__main__":
    _create_table()
