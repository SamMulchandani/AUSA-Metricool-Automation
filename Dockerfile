FROM python:3.12-slim

WORKDIR /src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /src/ ./src/

# Whatever your script's entrypoint file is
CMD ["python", "main.py"]