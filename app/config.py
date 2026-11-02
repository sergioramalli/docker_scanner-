import os
from dotenv import load_dotenv

load_dotenv()

API_HOST = os.environ["API_HOST"]
API_PORT = int(os.environ["API_PORT"])

SCANNER_HOST = os.environ["SCANNER_HOST"]
SCANNER_PORT = int(os.environ["SCANNER_PORT"])
SCANNER_URL = os.environ["SCANNER_URL"]
DOCKERFILE_SCANNER_URL = os.environ["DOCKERFILE_SCANNER_URL"]