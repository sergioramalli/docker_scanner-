FROM aquasec/trivy:0.76.1 AS trivy

FROM python:3.13-slim

WORKDIR /app

COPY --from=trivy /usr/local/bin/trivy /usr/local/bin/trivy

COPY docker/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY mock_scanner/ ./mock_scanner/
