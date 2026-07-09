from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"


def generate_html_report(evidence_dir: Path, context: dict) -> Path:
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=select_autoescape(["html", "xml"]))
    template = env.get_template("report.html")
    html = template.render(**context)
    out = evidence_dir / "final-report.html"
    out.write_text(html, encoding="utf-8")
    return out
