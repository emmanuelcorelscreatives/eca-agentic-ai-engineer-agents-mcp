FROM python:3.12-slim
WORKDIR /app
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt
COPY trading_floor.py api.py approve_order.py ./
COPY fixtures ./fixtures
RUN useradd --uid 10001 --create-home academy && mkdir /data && chown academy /data
USER academy
ENV ACADEMY_PAPER_DB=/data/paper.sqlite
EXPOSE 8000
CMD ["uvicorn","api:app","--host","0.0.0.0","--port","8000"]
