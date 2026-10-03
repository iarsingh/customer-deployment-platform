FROM python:3.12-slim

WORKDIR /app
COPY platform-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY platform-api/app ./app
COPY portal /portal

ENV PYTHONPATH=/app
ENV PLATFORM_PORTAL=/portal
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
