import docker
import tempfile
from pathlib import Path

import json
import math
from requests.exceptions import ReadTimeout

import io
import tarfile

from contextlib import ExitStack

def build_image(dockerfile_content: str, job_id: str) -> str:
    client = docker.from_env()

    try:
        with tempfile.TemporaryDirectory() as build_dir:
            dockerfile_path = Path(build_dir) / "Dockerfile"

            dockerfile_path.write_text(
                dockerfile_content,
                encoding="utf-8"
            )

            image, logs = client.images.build(
                path=build_dir,
                tag=f"job-{job_id}:latest",
                rm=True
            )

            return image.id
    finally:
        client.close()



def run_container(image_id: str) -> float:
    with ExitStack() as cleanup:
        client = docker.from_env()
        cleanup.callback(client.close)

        # Create volume
        volume = client.volumes.create()
        cleanup.callback(volume.remove)

        # Run container
        container = client.containers.run(
            image_id,
            detach=True,
            volumes={volume.name: {"bind": "/data", "mode": "rw"}},
            network_disabled=True,
            mem_limit="512m",
            pids_limit=100
        )
        cleanup.callback(container.remove, force=True)

        # Wait for completion
        if container.wait(timeout=60)["StatusCode"] != 0:
            raise RuntimeError("Container execution failed")

        # Retrieve performance file
        chunks, info = container.get_archive("/data/perf.json")

        with tarfile.open(
            fileobj=io.BytesIO(b"".join(chunks)),
            mode="r:"
        ) as archive:
            file = archive.extractfile("perf.json")
            if file is None:
                raise ValueError("Missing perf.json")

            perf = json.load(file)["perf"]

        if type(perf) not in (int, float) or not math.isfinite(perf):
            raise ValueError("Invalid performance value")

        return float(perf)


def remove_image(job_id: str) -> None:
    client = docker.from_env()

    try:
        image_tag = f"job-{job_id}:latest"
        client.images.remove(
            image=image_tag,
            force=False
        )
    finally:
        client.close()