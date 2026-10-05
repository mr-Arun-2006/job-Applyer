from app.matching import match_job_to_profile

def customize_resume(job, profile, base_resume_text: str) -> str:
    """Create a role-focused resume draft without inventing qualifications."""
    match = match_job_to_profile(job, profile)
    keywords = ", ".join(match["matched_keywords"][:20])
    header = f"TARGET ROLE: {job.get('title', '')} | {job.get('company', '')}\n"
    focus = f"ROLE-RELEVANT KEYWORDS: {keywords}\n\n"
    return header + focus + base_resume_text
