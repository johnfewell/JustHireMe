---
title: Lightweight Lead Harvester PRD
version: 0.1
date_created: 2026-05-09
last_updated: 2026-05-09
owner: Product/Engineering
tags: [design, prd, scraper, cli, dashboard, rezi]
---

# Introduction

This document defines a lightweight replacement concept for the current JustHireMe application. The new product focuses on scraping and triaging job or opportunity leads, with resume generation and resume storage delegated to Rezi through its MCP server.

The product is intentionally smaller than a local-first desktop career workbench. It is a CLI-first lead pipeline with a small dashboard and time-aware scan behavior.

## 1. Purpose & Scope

The product shall help a user discover relevant opportunities from configured sources, normalize and score those opportunities, review them in a small inbox, and hand selected opportunities to Rezi for resume work.

The product shall not attempt to be a full resume editor, local-first desktop app, graph-based profile database, or automated application bot.

Intended audience:

- Individual job seekers who want a repeatable lead discovery workflow.
- Developers/operators who prefer CLI workflows but want a lightweight dashboard for review.
- Users who already trust Rezi for resume management and generation.

Assumptions:

- Rezi MCP is available to the user and the user has the required Rezi account access.
- Scraping is the primary user value.
- A simple hosted or local service is acceptable; local-first is not a product requirement.

## 2. Definitions

- **Lead**: A job, contract, freelance, or opportunity record discovered from a source.
- **Source**: A configured website, feed, API, job board, or custom scraper target.
- **Scan**: A run that fetches, parses, normalizes, deduplicates, and stores leads from one or more sources.
- **Lead inbox**: A review queue containing new, kept, rejected, stale, or exported leads.
- **Time awareness**: Product behavior that uses timestamps, schedules, freshness windows, and run history.
- **Rezi MCP**: Rezi's remote Model Context Protocol server used to list, read, and write resumes.
- **MCP**: Model Context Protocol, a protocol for exposing tools and data to AI clients and applications.
- **CLI**: Command-line interface.
- **Dashboard**: A small web interface for monitoring sources and reviewing leads.

## 3. Requirements, Constraints & Guidelines

### Product Requirements

- **REQ-001**: The product shall provide a CLI for scanning sources, listing leads, scoring leads, reviewing leads, exporting leads, and sending selected leads to Rezi.
- **REQ-002**: The product shall provide a small dashboard for lead review, source status, and schedule visibility.
- **REQ-003**: The product shall support scheduled scans with explicit timezone handling.
- **REQ-004**: The product shall track when each lead was first seen, last seen, last scored, last reviewed, and exported.
- **REQ-005**: The product shall deduplicate leads by URL and by normalized company/title/source combinations.
- **REQ-006**: The product shall score leads using explainable criteria, not opaque ranking only.
- **REQ-007**: The product shall allow users to keep, reject, archive, or export a lead.
- **REQ-008**: The product shall integrate with Rezi MCP for resume handoff.
- **REQ-009**: The product shall store only Rezi identifiers or links for Rezi-managed resumes, not duplicate Rezi as a local resume database.
- **REQ-010**: The product shall provide a daily or per-run digest of new and high-priority leads.

### Non-Goals

- **NGO-001**: The product shall not implement a local resume PDF renderer.
- **NGO-002**: The product shall not implement a full resume editor.
- **NGO-003**: The product shall not require a Tauri desktop shell.
- **NGO-004**: The product shall not require Kuzu, LanceDB, or graph/vector storage for the MVP.
- **NGO-005**: The product shall not implement browser auto-apply as an MVP feature.
- **NGO-006**: The product shall not expose its own MCP server in the MVP unless needed by an external client.
- **NGO-007**: The product shall not optimize for local-first sync.

### Constraints

- **CON-001**: The MVP shall use a simple relational datastore, preferably SQLite for local/dev or Postgres for hosted deployments.
- **CON-002**: Source connector failures shall not fail an entire multi-source scan.
- **CON-003**: Scrapers shall record enough source metadata to debug parsing and deduplication decisions.
- **CON-004**: The system shall preserve raw source URL and retrieval timestamp for each lead.
- **CON-005**: The dashboard shall remain optional; all core workflows shall be possible through the CLI.

### Guidelines

- **GUD-001**: Prefer boring infrastructure over platform complexity.
- **GUD-002**: Prefer source-specific connectors over a large generic browser automation layer.
- **GUD-003**: Add browser automation only for sources that cannot be accessed reliably through HTTP, RSS, APIs, exports, or lightweight scraping.
- **GUD-004**: Keep resume-specific logic behind a Rezi integration boundary.
- **GUD-005**: Treat the previous JustHireMe app as a prototype and reference library, not as the foundation.

## 4. Interfaces & Data Contracts

### CLI Commands

The CLI shall support these commands in the MVP:

```bash
lead scan --source <source-id>
lead scan --all
lead inbox --new
lead list --status kept
lead show <lead-id>
lead keep <lead-id>
lead reject <lead-id> --reason "<reason>"
lead score <lead-id>
lead digest --today
lead send-to-rezi <lead-id> --resume <base-resume-id>
lead sources list
lead sources test <source-id>
lead schedule list
lead schedule set <source-id> --cron "0 8 * * 1-5" --timezone "America/Toronto"
```

### Dashboard Views

| View | Purpose | Required Actions |
| --- | --- | --- |
| Inbox | Review new and scored leads | keep, reject, archive, open source URL, send to Rezi |
| Lead Detail | Inspect normalized data and scoring rationale | edit notes, rescore, send to Rezi |
| Sources | Inspect configured sources and health | run now, test, enable, disable |
| Schedule | Inspect next scan times and recent runs | pause, resume, run now |
| Digest | Review new leads since last run or current day | keep, reject, export |

### Lead Data Model

```json
{
  "id": "lead_123",
  "source_id": "hn_whos_hiring",
  "source_url": "https://example.com/job",
  "canonical_url": "https://example.com/job",
  "title": "Senior Backend Engineer",
  "company": "Example Co",
  "location": "Remote",
  "description": "Raw or cleaned job description",
  "employment_type": "full_time",
  "compensation": "$140k-$180k",
  "status": "new",
  "score": 82,
  "score_reason": "Strong backend/Python match; remote; recent posting.",
  "score_factors": [
    {"name": "skill_match", "value": 35},
    {"name": "freshness", "value": 15}
  ],
  "first_seen_at": "2026-05-09T12:30:00-04:00",
  "last_seen_at": "2026-05-09T12:30:00-04:00",
  "last_scored_at": "2026-05-09T12:31:00-04:00",
  "expires_at": "2026-05-23T12:30:00-04:00",
  "rezi_resume_id": null,
  "notes": ""
}
```

### Source Data Model

```json
{
  "id": "hn_whos_hiring",
  "name": "Hacker News Who is Hiring",
  "type": "html",
  "enabled": true,
  "schedule": "0 8 * * 1-5",
  "timezone": "America/Toronto",
  "last_run_at": "2026-05-09T08:00:00-04:00",
  "next_run_at": "2026-05-12T08:00:00-04:00",
  "last_status": "ok",
  "last_error": ""
}
```

### Rezi Integration Interface

The product shall wrap Rezi MCP behind an internal service interface:

```python
class ReziClient:
    def list_resumes(self) -> list[dict]: ...
    def read_resume(self, resume_id: str) -> dict: ...
    def write_resume(self, resume: dict) -> dict: ...
    def create_resume_for_lead(self, lead: dict, base_resume_id: str, instructions: str = "") -> dict: ...
```

The Rezi integration shall use these capabilities:

- List available resumes.
- Read a selected base resume.
- Create or update a resume tailored to a selected lead.
- Return the Rezi resume identifier and relevant metadata to the lead record.

## 5. Acceptance Criteria

- **AC-001**: Given an enabled source, when the user runs `lead scan --source <source-id>`, then the system stores normalized leads and records a scan run.
- **AC-002**: Given duplicate URLs across scans, when a later scan finds the same URL, then the system updates `last_seen_at` instead of creating a duplicate lead.
- **AC-003**: Given a lead in the inbox, when the user runs `lead keep <lead-id>`, then the lead status becomes `kept`.
- **AC-004**: Given a lead in the inbox, when the user rejects it with a reason, then the lead status becomes `rejected` and the reason is stored.
- **AC-005**: Given a configured Rezi account, when the user runs `lead send-to-rezi <lead-id> --resume <base-resume-id>`, then the system creates or updates a Rezi resume and stores the returned Rezi identifier on the lead.
- **AC-006**: Given a source schedule and timezone, when the scheduled time arrives, then the system runs a scan for that source and records success or failure.
- **AC-007**: Given a stale lead older than its freshness window, when the inbox is shown, then the lead is marked stale or excluded from the default new inbox.
- **AC-008**: Given the dashboard is unavailable, when the user uses the CLI, then all core workflows remain possible.

## 6. Test Automation Strategy

- **Test Levels**: Unit, integration, and minimal end-to-end tests.
- **Unit Tests**:
  - Source parser normalization.
  - Deduplication rules.
  - Scoring factor calculations.
  - Time-window and staleness rules.
  - Rezi client request/response mapping with fake MCP responses.
- **Integration Tests**:
  - Scan run writes leads and scan metadata.
  - Rezi handoff updates a lead with a Rezi resume ID.
  - Dashboard API returns inbox and source health.
- **End-to-End Tests**:
  - Run a local scan against fixture HTML/API responses.
  - Review a lead through the dashboard.
  - Send a fixture lead to a fake Rezi server.
- **Test Data Management**:
  - Use fixture source pages and fixture Rezi MCP responses.
  - Do not run live scraping or live Rezi calls in default CI.
- **Coverage Requirements**:
  - Parser, dedupe, scoring, and time-rule modules should have high unit coverage.
  - Dashboard visual coverage is secondary to workflow/API coverage.

## 7. Rationale & Context

The previous JustHireMe prototype explored a broad local-first career workbench: desktop shell, local resume generation, graph storage, vector storage, background sidecar, MCP server, profile management, and browser automation.

The resulting lesson is that the interesting product value is scraping and lead discovery, not local-first resume management. Rezi can own resume generation and resume storage. The new product should therefore reduce scope and optimize for the lead pipeline:

1. Discover leads.
2. Normalize and score leads.
3. Review leads quickly.
4. Hand selected leads to Rezi.

This reduces implementation complexity and avoids building a weaker local duplicate of specialized resume tooling.

## 8. Dependencies & External Integrations

### External Systems

- **EXT-001**: Rezi MCP - Remote MCP server for resume list/read/write operations.
- **EXT-002**: Job/opportunity sources - Websites, feeds, APIs, or exports that provide leads.

### Third-Party Services

- **SVC-001**: Rezi - Required for resume handoff and resume generation/storage.
- **SVC-002**: Optional scraping providers - May be used for sources that require browser rendering or anti-bot handling.

### Infrastructure Dependencies

- **INF-001**: Relational database - SQLite for simple local usage or Postgres for hosted usage.
- **INF-002**: Scheduler - Cron, system timer, hosted scheduler, or lightweight application scheduler.
- **INF-003**: Dashboard runtime - Simple web server capable of serving lead inbox and source status.

### Technology Platform Dependencies

- **PLT-001**: CLI runtime - Python or Node.js is acceptable; choose based on scraper ecosystem and deployment preference.
- **PLT-002**: Web dashboard - Minimal frontend stack; avoid desktop-only dependencies.

## 9. Examples & Edge Cases

### Example Workflow

```bash
lead sources list
lead scan --source hn_whos_hiring
lead inbox --new
lead keep lead_123
lead send-to-rezi lead_123 --resume resume_base_456
lead digest --today
```

### Edge Cases

- A source is unavailable: record scan failure and continue scanning other sources.
- A lead appears under multiple URLs: dedupe by canonical URL first, then by normalized company/title/source.
- A lead has no company: store it, but reduce confidence and flag it for review.
- A lead is old but newly discovered: keep both `first_seen_at` and any source-posted date if available.
- Rezi MCP authentication fails: keep the lead unchanged and show a clear action-required error.
- Rezi write succeeds but local update fails: retry local persistence with the returned Rezi ID; log the handoff result.

## 10. Validation Criteria

- The MVP can run a scan from the CLI and populate the inbox.
- The MVP can show new leads in both CLI and dashboard.
- The MVP can deduplicate repeated scan results.
- The MVP can score leads with an explanation.
- The MVP can send a selected lead to Rezi through an integration boundary.
- The MVP can run scheduled scans with timezone-aware next-run timestamps.
- The MVP does not include local resume PDF generation, Kuzu, LanceDB, Tauri, or browser auto-apply as required components.

## 11. Related Specifications / Further Reading

- Rezi Resume MCP Server documentation: https://www.rezi.ai/rezi-docs/resume-mcp-server
- Existing JustHireMe prototype repository modules:
  - `backend/agents/lead_intel.py`
  - `backend/agents/quality_gate.py`
  - `backend/agents/scoring_engine.py`
  - `backend/agents/scout.py`
