FROM ubuntu:24.04

RUN useradd -m appuser \
    && mkdir -p /data \
    && chown appuser:appuser /data

USER appuser

CMD ["sh", "-c", "echo '{\"perf\":0.99}' > /data/perf.json && sleep 10"]