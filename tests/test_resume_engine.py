from __future__ import annotations

from app.resume_engine import ATSResumeEngine


def test_render_and_extract_docx(tmp_path):
    engine = ATSResumeEngine()
    output = engine.render_docx(
        """Arun K
arun@example.com | Tamil Nadu

PROFESSIONAL SUMMARY
Data engineer focused on Python and SQL.

SKILLS
Python
SQL

PROJECTS
Job automation system
""",
        "Example Company",
        "Data Engineer",
        str(tmp_path),
    )

    extracted = engine.extract_text(output)

    assert "Arun K" in extracted
    assert "PROFESSIONAL SUMMARY" in extracted
    assert "Data engineer" in extracted
