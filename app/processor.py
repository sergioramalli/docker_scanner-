import logging

from app.models import JobStatus
from app.job_store import get_job
from app.docker_service import build_image, run_container, remove_image
from app.scanner_service import scan_image
from app.scanner_service import scan_image, scan_dockerfile

logger = logging.getLogger(__name__)


def process_job(job_id: str, dockerfile: str):
    job = get_job(job_id)

    if job is None:
        return

    try:

        job.status = JobStatus.CHECKING_DOCKERFILE

        if not scan_dockerfile(dockerfile):
            job.status = JobStatus.FAILED
            job.error = "Dockerfile security scan failed"
            return

        job.status = JobStatus.BUILDING
        image_id = build_image(dockerfile, job_id)
        job.image_id = image_id

        job.status = JobStatus.SCANNING

        if not scan_image(image_id):
            job.status = JobStatus.FAILED
            job.error = "Vulnerability scan failed"
            return

        job.status = JobStatus.RUNNING
        job.performance = run_container(image_id)
        job.status = JobStatus.SUCCESS

    except Exception as e:
        job.status = JobStatus.FAILED
        job.error = str(e)

    finally:
        if job.image_id is not None:
            try:
                remove_image(job_id)
            except Exception:
                logger.exception(
                    "Image cleanup failed for job %s",
                    job_id
                )
