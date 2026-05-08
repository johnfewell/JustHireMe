from __future__ import annotations


def graph_stats() -> dict:
    from db.client import graph_counts

    return graph_counts()


def get_profile() -> dict:
    from db.client import get_profile as _get_profile

    return _get_profile()


def update_candidate_profile(name: str, summary: str) -> dict:
    if not name.strip() and not summary.strip():
        raise ValueError("Name or summary is required")
    from db.client import update_candidate

    return update_candidate(name, summary)


def add_profile_skill(name: str, category: str) -> dict:
    if not name.strip():
        raise ValueError("Skill name is required")
    from db.client import add_skill

    return add_skill(name, category)


def update_profile_skill(skill_id: str, name: str, category: str) -> dict:
    if not name.strip():
        raise ValueError("Skill name is required")
    from db.client import update_skill

    return update_skill(skill_id, name, category)


def delete_profile_skill(skill_id: str) -> dict:
    from db.client import delete_skill

    delete_skill(skill_id)
    return {"ok": True}


def add_profile_experience(role: str, company: str, period: str, description: str) -> dict:
    if not role.strip() and not company.strip():
        raise ValueError("Role or company is required")
    from db.client import add_experience

    return add_experience(role, company, period, description)


def update_profile_experience(
    experience_id: str,
    role: str,
    company: str,
    period: str,
    description: str,
) -> dict:
    if not role.strip() and not company.strip():
        raise ValueError("Role or company is required")
    from db.client import update_experience

    return update_experience(experience_id, role, company, period, description)


def delete_profile_experience(experience_id: str) -> dict:
    from db.client import delete_experience

    delete_experience(experience_id)
    return {"ok": True}


def add_profile_project(title: str, stack: str, repo: str, impact: str) -> dict:
    if not title.strip():
        raise ValueError("Project title is required")
    from db.client import add_project

    return add_project(title, stack, repo, impact)


def update_profile_project(project_id: str, title: str, stack: str, repo: str, impact: str) -> dict:
    if not title.strip():
        raise ValueError("Project title is required")
    from db.client import update_project

    return update_project(project_id, title, stack, repo, impact)


def delete_profile_project(project_id: str) -> dict:
    from db.client import delete_project

    delete_project(project_id)
    return {"ok": True}
