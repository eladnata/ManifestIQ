from __future__ import annotations

from pathlib import Path


IGNORED_FIXTURES = {
    Path("tests/sample_projects/structure-risky/sample.db"): b"synthetic database fixture\n",
    Path("tests/sample_projects/structure-risky/bundle.zip"): b"PK\x03\x04 synthetic archive fixture\n",
    Path("tests/sample_projects/operational-risky/local.db"): b"synthetic operational data fixture\n",
    Path("tests/sample_projects/operational-risky/.env"): b"ENVIRONMENT=production\nAPI_KEY=fake-test-key\n",
}


def pytest_sessionstart(session):
    created = []
    for path, content in IGNORED_FIXTURES.items():
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        created.append(path)
    session.config._manifestiq_created_ignored_fixtures = created


def pytest_sessionfinish(session, exitstatus):
    for path in getattr(session.config, "_manifestiq_created_ignored_fixtures", []):
        try:
            path.unlink()
        except FileNotFoundError:
            pass
