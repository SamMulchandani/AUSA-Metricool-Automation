# docker buildx build --platform linux/amd64 --no-cache -t us-central1-docker.pkg.dev/ausa-data-automation-506918/docker-repo/ausa:latest --push .

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Whatever your script's entrypoint file is
CMD ["python", "src/main.py"]