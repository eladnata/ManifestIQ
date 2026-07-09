FROM python:3.12-slim
COPY src /app/src
HEALTHCHECK CMD python -c "from src.app import health; health()"
CMD ["python", "-m", "src.app"]
