from __future__ import annotations

import os


def get_events(limit: int = 100, job_id: str | None = None) -> list[dict]:
    from db.client import get_events as _get_events

    return _get_events(limit=limit, job_id=job_id)


def prepare_pipeline_state(job_id: str) -> dict:
    from db.client import get_lead_by_id, get_profile, get_settings

    lead = get_lead_by_id(job_id)
    if not lead:
        raise LookupError("lead not found")
    return {
        "job_id": job_id,
        "lead": lead,
        "profile": get_profile(),
        "cfg": get_settings(),
        "score": 0,
        "reason": "",
        "match_points": [],
        "gaps": [],
        "asset_path": "",
        "cover_letter_path": "",
        "error": None,
    }


def resolve_lead_pdf(
    job_id: str,
    kind: str = "resume",
    version: int | None = None,
    appdata_root: str | None = None,
) -> tuple[str, str]:
    from db.client import get_lead_by_id

    lead = get_lead_by_id(job_id)
    if not lead:
        raise LookupError("Lead not found")
    is_cover = kind in {"cover", "cover_letter", "cover-letter"}
    missing = "Cover letter not generated yet" if is_cover else "Resume not generated yet"
    if version is not None:
        paths = [
            lead.get("resume_asset") or lead.get("asset") or "",
            lead.get("cover_letter_asset") or "",
        ]
        base_dir = next((os.path.dirname(path) for path in paths if path), None)
        if not base_dir:
            root = appdata_root or os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
            base_dir = os.path.join(root, "JustHireMe", "assets")
        filename = f"{job_id}_cl_v{version}.pdf" if is_cover else f"{job_id}_v{version}.pdf"
        path = os.path.join(base_dir, filename)
    elif is_cover:
        path = lead.get("cover_letter_asset") or ""
        filename = f"{job_id}_cover_letter.pdf"
    else:
        path = lead.get("resume_asset") or lead.get("asset") or ""
        filename = f"{job_id}_resume.pdf"
    if not path or not os.path.exists(path):
        raise FileNotFoundError(missing)
    return path, filename
