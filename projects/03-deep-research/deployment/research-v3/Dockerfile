# Context: projects/03-deep-research. Central QA must provide real requirements.lock.
FROM python:3.12-slim
WORKDIR /app
COPY deployment/research-v3/requirements.lock /tmp/requirements.lock
RUN pip install --no-cache-dir --require-hashes -r /tmp/requirements.lock
RUN useradd --create-home --uid 10001 academy
COPY research_lab /app/research_lab
COPY data /app/data
USER academy
ENV ACADEMY_STATE_DIR=/state PYTHONUNBUFFERED=1
EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:7860/healthz',timeout=2)"
CMD ["uvicorn","research_lab.deploy_v3:create_app","--factory","--host","0.0.0.0","--port","7860"]
