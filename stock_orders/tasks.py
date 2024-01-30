from celery import shared_task
from stock_orders.sse_service import AlpacaSSEService
import logging

logger = logging.getLogger(__name__)


@shared_task
def listen_to_alpaca_sse():
    logger.info("Задача SSE запущена")
    sse_url = \
        'https://broker-api.sandbox.alpaca.markets/v2beta1/events/trades'
    try:
        service = AlpacaSSEService()
        service.listen_events(sse_url)
        logger.info("Подключение к SSE-серверу успешно")
    except Exception as e:
        logger.error(f"Ошибка при подключении к SSE-серверу: {e}")
