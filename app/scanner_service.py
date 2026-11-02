import httpx
from app.config import SCANNER_URL
from app.config import DOCKERFILE_SCANNER_URL

def scan_image(image_id: str) -> bool:
    response = httpx.post(
        SCANNER_URL,
        json={"image_id": image_id},
        timeout=10.0
    )

    response.raise_for_status()

    result = response.json()

    if not isinstance(result.get("safe"), bool):
        raise ValueError("Invalid scanner response")

    return result["safe"]

def scan_dockerfile(dockerfile: str) -> bool:
    response = httpx.post(
        DOCKERFILE_SCANNER_URL,
        json={"dockerfile": dockerfile},
        timeout=180.0
    )

    response.raise_for_status()

    result = response.json()

    if not isinstance(result.get("safe"), bool):
        raise ValueError("Invalid Dockerfile scanner response")

    return result["safe"]