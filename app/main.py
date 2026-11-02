from uuid import uuid4

from fastapi import FastAPI, HTTPException, Response, Body, status

from app.models import Job, JobStatus
from app.job_store import create_job, get_job

from fastapi import BackgroundTasks
from app.processor import process_job

app = FastAPI()

@app.post("/jobs", response_model=Job, status_code=202)
def submit_job(
    background_tasks: BackgroundTasks,
    dockerfile: str = Body(media_type="text/plain")
):
    job = Job(
        job_id=str(uuid4()),
        status=JobStatus.PENDING
    )

    create_job(job)

    background_tasks.add_task(
        process_job,
        job.job_id,
        dockerfile
    )

    return job

@app.get("/jobs/{job_id}", response_model=Job)
def retrieve_job(job_id: str):
    job = get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job