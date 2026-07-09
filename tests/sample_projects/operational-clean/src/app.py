import logging
import os
import requests

logger = logging.getLogger(__name__)


def health():
    return {"status": "ok"}


def call_service():
    try:
        response = requests.get(os.environ["SERVICE_URL"], timeout=5)
        response.raise_for_status()
        logger.info("request completed", extra={"correlation_id": "sample"})
        return response.json()
    except requests.RequestException:
        logger.exception("request failed")
        raise
