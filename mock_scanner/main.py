import json
import logging
import subprocess
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import os
from urllib.parse import urlparse

IMAGE_SCAN_PATH = urlparse(os.environ["SCANNER_URL"]).path
DOCKERFILE_SCAN_PATH = urlparse(os.environ["DOCKERFILE_SCANNER_URL"]).path

app = FastAPI()
logger = logging.getLogger(__name__)


class ImageScanRequest(BaseModel):
    image_id: str


class DockerfileScanRequest(BaseModel):
    dockerfile: str


@app.post(IMAGE_SCAN_PATH)
def scan_image(request: ImageScanRequest):
    try:
        result = subprocess.run(
            [
                "trivy", "image",
                "--image-src", "docker",
                "--scanners", "vuln",
                "--severity", "HIGH,CRITICAL",
                "--format", "json",
                "--quiet",
                request.image_id,
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=240,
        )
        report = json.loads(result.stdout)
        vulnerabilities = sum(
            len(item.get("Vulnerabilities") or [])
            for item in report.get("Results", [])
        )
        return {"safe": vulnerabilities == 0, "vulnerabilities": vulnerabilities}

    except subprocess.TimeoutExpired as exc:
        raise HTTPException(status_code=504, detail="Image scan timed out") from exc
    except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        logger.exception("Trivy image scan failed")
        raise HTTPException(status_code=502, detail="Image scan failed") from exc


@app.post(DOCKERFILE_SCAN_PATH)
def scan_dockerfile(request: DockerfileScanRequest):
    with tempfile.TemporaryDirectory() as directory:
        dockerfile_path = Path(directory) / "Dockerfile"
        dockerfile_path.write_text(request.dockerfile, encoding="utf-8")

        try:
            result = subprocess.run(
                [
                    "trivy", "config",
                    "--misconfig-scanners", "dockerfile",
                    "--severity", "HIGH,CRITICAL",
                    "--format", "json",
                    "--quiet",
                    str(dockerfile_path),
                ],
                capture_output=True,
                text=True,
                check=True,
                timeout=120,
            )
            report = json.loads(result.stdout)

            dockerfile_results = [
                item
                for item in report.get("Results", [])
                if item.get("Type") == "dockerfile"
            ]
            if not dockerfile_results:
                raise HTTPException(
                    status_code=502,
                    detail="Trivy did not scan the Dockerfile",
                )

            findings = sum(
                len(item.get("Misconfigurations") or [])
                for item in dockerfile_results
            )
            return {"safe": findings == 0, "misconfigurations": findings}

        except subprocess.TimeoutExpired as exc:
            raise HTTPException(status_code=504, detail="Dockerfile scan timed out") from exc
        except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
            logger.exception("Trivy Dockerfile scan failed")
            raise HTTPException(status_code=502, detail="Dockerfile scan failed") from exc
