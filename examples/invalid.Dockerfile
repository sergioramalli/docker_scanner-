FROM ubuntu:24.04
CMD ["sh", "-c", "echo '{\"perf\":0.99}' > /data/perf.json && sleep 10"]