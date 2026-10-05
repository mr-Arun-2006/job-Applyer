from sqlalchemy import select
from app.database import SessionLocal
from app.models import Job

def save_jobs(items):
    created = 0
    with SessionLocal() as session:
        for item in items:
            source = item["source"]
            source_job_id = item.get("source_job_id")
            if source_job_id:
                exists = session.scalar(select(Job).where(Job.source == source, Job.source_job_id == source_job_id))
                if exists:
                    continue
            session.add(Job(**item))
            created += 1
        session.commit()
    return created
