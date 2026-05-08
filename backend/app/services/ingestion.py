from __future__ import annotations

import json
from pathlib import Path


def import_profile_data(data: dict) -> dict:
    from db.client import (
        add_achievement,
        add_certification,
        add_education,
        add_experience,
        add_project,
        add_skill,
        save_settings,
        update_candidate,
    )

    errors = []
    stats = {k: 0 for k in [
        "skills", "experience", "projects", "education",
        "certifications", "achievements",
    ]}

    candidate = data.get("candidate") or {}
    if candidate.get("name") or candidate.get("summary"):
        try:
            update_candidate(candidate.get("name", ""), candidate.get("summary", ""))
        except Exception as exc:
            errors.append(f"candidate: {exc}")

    identity = data.get("identity") or {}
    for key in ["email", "phone", "linkedin_url", "github_url", "website_url", "city"]:
        value = identity.get(key)
        if value:
            try:
                save_settings({key: value})
            except Exception as exc:
                errors.append(f"identity.{key}: {exc}")

    for skill in data.get("skills") or []:
        try:
            add_skill(skill.get("name", ""), skill.get("category", "general"))
            stats["skills"] += 1
        except Exception:
            pass

    for exp in data.get("experience") or []:
        try:
            add_experience(
                exp.get("role", ""),
                exp.get("company", ""),
                exp.get("period", ""),
                exp.get("description", ""),
            )
            stats["experience"] += 1
        except Exception as exc:
            errors.append(f"exp {exp.get('role', '')}: {exc}")

    for project in data.get("projects") or []:
        try:
            add_project(
                project.get("title", ""),
                project.get("stack", ""),
                project.get("repo", ""),
                project.get("impact", ""),
            )
            stats["projects"] += 1
        except Exception as exc:
            errors.append(f"proj {project.get('title', '')}: {exc}")

    for entry in data.get("education") or []:
        try:
            add_education(entry.get("title", ""))
            stats["education"] += 1
        except Exception as exc:
            errors.append(f"edu: {exc}")

    for cert in data.get("certifications") or []:
        try:
            add_certification(cert.get("title", ""))
            stats["certifications"] += 1
        except Exception as exc:
            errors.append(f"cert: {exc}")

    for achievement in data.get("achievements") or []:
        try:
            add_achievement(achievement.get("title", ""))
            stats["achievements"] += 1
        except Exception as exc:
            errors.append(f"achievement: {exc}")

    return {
        "status": "ok" if not errors else "partial",
        "stats": stats,
        "errors": errors,
    }


def load_profile_template(backend_root: Path) -> dict:
    template_path = backend_root / "data" / "profile_schema_example.json"
    with open(template_path, encoding="utf-8") as handle:
        return json.load(handle)
