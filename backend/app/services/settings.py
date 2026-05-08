from __future__ import annotations

MASK = "••••••••••••••••••••"


def sensitive_keys(values: dict) -> set[str]:
    fixed = {"anthropic_key", "linkedin_cookie", "x_bearer_token", "custom_connector_headers"}
    dynamic = {
        key
        for key in values
        if key.endswith("_api_key") or key.endswith("_key") or key.endswith("_token")
    }
    return fixed | dynamic


def read_masked_settings() -> dict:
    from db.client import get_settings

    settings = get_settings()
    for key in sensitive_keys(settings):
        if settings.get(key):
            settings[key] = MASK
    return settings


def prepare_settings_payload(values: dict) -> dict[str, str]:
    return {key: "" if value is None else str(value) for key, value in values.items()}


def save_settings_payload(values: dict) -> dict:
    from db.client import get_settings, save_settings

    payload = prepare_settings_payload(values)
    old = get_settings()
    for key in sensitive_keys({**old, **payload}):
        if payload.get(key) == MASK:
            payload[key] = old.get(key, "")
    save_settings(payload)
    return payload


def get_resume_template() -> dict:
    from db.client import get_setting

    return {"template": get_setting("resume_template", "")}


def save_resume_template(template: str) -> dict:
    from db.client import save_settings

    save_settings({"resume_template": template})
    return {"ok": True}
