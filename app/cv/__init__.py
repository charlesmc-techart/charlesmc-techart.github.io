"""Package for working with the curriculum vitae page"""

from typing import Any

from flask import Blueprint, render_template

from .db import Table, close_db, fetch_data, get_db, read_sql_file

bp = Blueprint("cv", __name__, template_folder="templates", url_prefix="/cv")

bp.teardown_request(close_db)


def transform_experience_data(
    raw_data: Table,
) -> dict[str, dict[str, dict[str, Any]]]:
    result: dict[str, dict[str, dict[str, Any]]] = {}

    employer: str
    job_details: list[str]
    for employer, *job_details in raw_data:
        if employer not in result:
            result[employer] = {}
        current_employer = result[employer]

        job_title, start_date, end_date, highlights = job_details
        if job_title not in current_employer:
            current_employer[job_title] = {
                "start_date": start_date,
                "end_date": end_date,
            }
        current_job_title = current_employer[job_title]

        if not highlights:
            continue

        if "highlights" not in current_job_title:
            current_job_title["highlights"] = []

        current_job_title["highlights"].append(highlights)

    return result


def transform_projects_data(raw_data: Table) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}

    project: str
    project_type: str
    url: str
    project_details: list[str]
    for project, project_type, url, *project_details in raw_data:
        if project not in result:
            result[project] = {"type": project_type, "url": url, "roles": {}}
        current_project = result[project]

        roles, start_date, end_date, highlights = project_details
        if roles not in current_project["roles"]:
            current_project["roles"][roles] = {
                "start_date": start_date,
                "end_date": end_date,
            }
        current_roles = current_project["roles"][roles]

        if not highlights:
            continue

        if "highlights" not in current_roles:
            current_roles["highlights"] = []

        current_roles["highlights"].append(highlights)

    return result


def transform_skills_data(raw_data: Table) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}

    category: str
    skill: str
    for category, skill in raw_data:
        if category not in result:
            result[category] = []

        result[category].append(skill)

    return result


def transform_education_data(raw_data: Table) -> dict[str, list[list[str]]]:
    result: dict[str, list[list[str]]] = {}

    school: str
    concentration: list[str]
    for school, *concentration in raw_data:
        if school not in result:
            result[school] = []

        result[school].append(concentration)

    return result


def fetch_from_db() -> dict[str, dict[str, Any]]:
    cur = get_db().cursor()

    experience_sql = read_sql_file("experience.sql")
    experience_raw_data = fetch_data(cur, experience_sql)
    experience = transform_experience_data(experience_raw_data)

    projects_sql = read_sql_file("projects.sql")
    projects_raw_data = fetch_data(cur, projects_sql)
    projects = transform_projects_data(projects_raw_data)

    skills_sql = read_sql_file("skills.sql")
    skills_raw_data = fetch_data(cur, skills_sql)
    skills = transform_skills_data(skills_raw_data)

    education_sql = read_sql_file("education.sql")
    education_raw_data = fetch_data(cur, education_sql)
    education = transform_education_data(education_raw_data)

    return {
        "experience": experience,
        "projects": projects,
        "skills": skills,
        "education": education,
    }


@bp.get("")
def view() -> str:
    data = fetch_from_db()

    return render_template("cv/all.html", **data)
