FROM python:3.12-slim
WORKDIR /app
COPY requirements-optional.txt ./
RUN pip install --no-cache-dir -r requirements-optional.txt
COPY . .
RUN useradd --create-home academy
USER academy
ENV GRADIO_SERVER_NAME=0.0.0.0
EXPOSE 7860
CMD ["python", "app.py"]
