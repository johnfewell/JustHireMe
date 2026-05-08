from __future__ import annotations

import csv
import io
import os
import re


def annotate_job_lead(lead: dict) -> dict:
    from agents.scout import classify_job_seniority

    meta = dict(lead.get("source_meta") or {})
    level = str(meta.get("seniority_level") or lead.get("seniority_level") or "").strip().lower()
    if level not in {"fresher", "junior", "mid", "senior", "unknown"}:
        level = classify_job_seniority(lead)
    meta["seniority_level"] = level
    meta["is_beginner"] = level in {"fresher", "junior"}
    return {**lead, "source_meta": meta, "seniority_level": level}


def list_job_leads(beginner_only: bool = False, seniority: str | None = None) -> list[dict]:
    from db.client import get_all_leads

    jobs = [
        annotate_job_lead(lead)
        for lead in get_all_leads()
        if (lead.get("kind") or "job") == "job"
    ]
    requested = str(seniority or "").strip().lower()
    if beginner_only or requested == "beginner":
        return [lead for lead in jobs if lead.get("seniority_level") in {"fresher", "junior"}]
    if requested in {"fresher", "junior", "mid", "senior", "unknown"}:
        return [lead for lead in jobs if lead.get("seniority_level") == requested]
    return jobs


def export_leads_csv() -> str:
    from db.client import get_all_leads

    fields = [
        "job_id", "title", "company", "url", "platform", "status",
        "score", "signal_score", "seniority_level", "location",
        "reason", "created_at",
    ]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(get_all_leads())
    return buf.getvalue()


def versioned_assets(job_id: str, base_dir: str) -> list[dict]:
    versions: dict[int, dict] = {}
    patterns = [
        ("resume", re.compile(rf"^{re.escape(job_id)}_v(\d+)\.pdf$")),
        ("cover_letter", re.compile(rf"^{re.escape(job_id)}_cl_v(\d+)\.pdf$")),
    ]
    try:
        names = os.listdir(base_dir)
    except Exception:
        return []
    for name in names:
        full = os.path.join(base_dir, name)
        if not os.path.isfile(full):
            continue
        for key, pattern in patterns:
            match = pattern.match(name)
            if match:
                version = int(match.group(1))
                versions.setdefault(version, {"version": version})[key] = full
    return [versions[v] for v in sorted(versions, reverse=True)]


def lead_versions(job_id: str, appdata_root: str) -> list[dict]:
    from db.client import get_lead_by_id

    lead = get_lead_by_id(job_id)
    if not lead:
        raise LookupError("Lead not found")
    paths = [
        lead.get("resume_asset") or lead.get("asset") or "",
        lead.get("cover_letter_asset") or "",
    ]
    base_dir = next((os.path.dirname(path) for path in paths if path), None)
    if not base_dir:
        base_dir = os.path.join(appdata_root, "JustHireMe", "assets")
    return versioned_assets(job_id, base_dir)


def get_job_lead(job_id: str) -> dict:
    from db.client import get_lead_by_id

    lead = get_lead_by_id(job_id)
    if not lead:
        raise LookupError("Lead not found")
    return annotate_job_lead(lead) if (lead.get("kind") or "job") == "job" else lead


def delete_job_lead(job_id: str) -> None:
    from db.client import delete_lead

    delete_lead(job_id)


def update_job_status(job_id: str, status: str) -> None:
    from db.client import update_lead_status

    update_lead_status(job_id, status)


def save_job_feedback(job_id: str, feedback: str, note: str = "") -> dict:
    from db.client import save_lead_feedback

    lead = save_lead_feedback(job_id, feedback, note)
    if not lead:
        raise LookupError("Lead not found")
    return lead


def update_job_followup(job_id: str, days: int) -> dict:
    from db.client import update_lead_followup

    lead = update_lead_followup(job_id, days)
    if not lead:
        raise LookupError("Lead not found")
    return lead


def create_manual_job_lead(text: str, url: str) -> dict:
    if not text.strip() and not url.strip():
        raise ValueError("Paste lead text or a URL")

    from agents.lead_intel import manual_lead_from_text
    from db.client import get_lead_by_id, rank_lead_by_feedback, save_lead

    lead = rank_lead_by_feedback(manual_lead_from_text(text, url, "job"))
    if lead.get("kind") != "job":
        raise TypeError("Only job leads are accepted right now")
    lead = annotate_job_lead(lead)
    save_lead(
        lead["job_id"],
        lead["title"],
        lead["company"],
        lead["url"],
        lead["platform"],
        lead["description"],
        kind=lead["kind"],
        budget=lead["budget"],
        signal_score=lead["signal_score"],
        signal_reason=lead["signal_reason"],
        signal_tags=lead["signal_tags"],
        outreach_reply=lead["outreach_reply"],
        outreach_dm=lead["outreach_dm"],
        outreach_email=lead.get("outreach_email", ""),
        proposal_draft=lead.get("proposal_draft", ""),
        fit_bullets=lead.get("fit_bullets", []),
        followup_sequence=lead.get("followup_sequence", []),
        proof_snippet=lead.get("proof_snippet", ""),
        tech_stack=lead.get("tech_stack", []),
        location=lead.get("location", ""),
        urgency=lead.get("urgency", ""),
        base_signal_score=lead.get("base_signal_score"),
        learning_delta=lead.get("learning_delta"),
        learning_reason=lead.get("learning_reason", ""),
        source_meta=lead["source_meta"],
    )
    return get_lead_by_id(lead["job_id"]) or lead


def due_followups(limit: int = 25) -> list[dict]:
    from db.client import get_due_followups

    return get_due_followups(limit)
