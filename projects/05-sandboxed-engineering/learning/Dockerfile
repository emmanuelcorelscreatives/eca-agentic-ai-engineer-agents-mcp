# Operator must supply actual locally available digest identities. No defaults
# pretend to be verified pins; central QA records the produced image digest.
ARG PYTHON_IMAGE
ARG UV_IMAGE
FROM ${UV_IMAGE} AS uv_binary
FROM ${PYTHON_IMAGE}
COPY --from=uv_binary /uv /usr/local/bin/uv
WORKDIR /opt/engineering
COPY offline-cache/ /opt/uv-cache/
ENV UV_CACHE_DIR=/opt/uv-cache UV_PYTHON_DOWNLOADS=never
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --offline --no-dev
COPY semantic_team.py crewai_roles.py container_entrypoint.py container_launch.py delivery_package.py ./
ENV PYTHONDONTWRITEBYTECODE=1 UV_OFFLINE=1
ENV PATH="/opt/engineering/.venv/bin:${PATH}"
USER 65534:65534
ENTRYPOINT []
CMD ["python", "-B", "/opt/engineering/container_entrypoint.py"]
