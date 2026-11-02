from enum import Enum
from pydantic import BaseModel


class JobStatus(str, Enum):
    PENDING = "pending"
    BUILDING = "building"
    BUILT = "built"
    SCANNING = "scanning"
    APPROVED = "approved"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CHECKING_DOCKERFILE = "checking_dockerfile"

class Job(BaseModel):
    job_id: str
    status: JobStatus
    performance: float | None = None
    error: str | None = None
    image_id: str | None = None