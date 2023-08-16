FROM python:3.10-slim-bullseye

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY simple_run.py .
COPY function_modules/ function_modules/
COPY data/ data/

ENTRYPOINT ["python", "simple_run.py"]
