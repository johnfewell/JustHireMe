from __future__ import annotations


def cleanup_bad_leads(dry_run: bool = False, limit: int = 1000) -> tuple[dict, list[dict]]:
    from db.client import cleanup_bad_leads as _cleanup_bad_leads
    from db.client import get_lead_by_id

    result = _cleanup_bad_leads(limit, dry_run)
    updated = []
    if not dry_run:
        for item in result.get("items", [])[:100]:
            lead = get_lead_by_id(item["job_id"])
            if lead:
                updated.append(lead)
    return result, updated


def cleanup_done_message(result: dict, dry_run: bool = False) -> str:
    action = "would discard" if dry_run else "discarded"
    return (
        f"Cleanup scanned {result['scanned']} leads and "
        f"{action} {result['candidates']} bad rows."
    )


def answer_help_question(question: str, history: list[dict]) -> dict:
    from agents.help_agent import answer

    return answer(question, history)
