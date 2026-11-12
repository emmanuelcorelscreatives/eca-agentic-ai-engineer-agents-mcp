FROM python:3.12-slim
WORKDIR /app
COPY requirements-optional.txt ./
RUN pip install --no-cache-dir -r requirements-optional.txt
COPY . .
RUN useradd --create-home academy && mkdir -p /data && chown academy:academy /data
USER academy
ENV TWIN_DATABASE=/data/twin.sqlite
EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s CMD python health.py --readiness || exit 1
CMD ["python", "app.py"]
