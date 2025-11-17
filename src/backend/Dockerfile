FROM python:3.10-slim
WORKDIR /app
COPY ./app /app
RUN pip install --no-cache-dir -r /app/../requirements.txt
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
