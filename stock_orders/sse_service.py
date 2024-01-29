import base64
import json
from sseclient import SSEClient
from django.conf import settings
from stock_orders.models import StockOrder
import logging

logger = logging.getLogger(__name__)


class AlpacaSSEService:
    def __init__(self):
        self.api_key = settings.BROKER_API_KEY
        self.secret_key = settings.BROKER_SECRET_KEY

    def get_credentials(self):
        credentials = f'{self.api_key}:{self.secret_key}'
        return base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    def connect(self, url):
        headers = {
            "Accept": "text/event-stream",
            "Authorization": f'Basic {self.get_credentials()}'
        }
        return SSEClient(url, headers=headers)

    def process_event(self, event_data):
        try:
            data = json.loads(event_data)
            logger.info(f"Получены данные события: {data}")

            order_data = data.get('order', {})
            order_id = order_data.get('id')
            if not order_id:
                logger.error(f"Отсутствует ID ордера в данных: {data}")
                return

            status = order_data.get('status')
            if not status:
                logger.error(
                    f"Отсутствует статус в ордерах: {order_data}"
                )
                return

            try:
                order = StockOrder.objects.get(id_order=order_id)
                order.status = status
                order.save()
                logger.info(
                    f"Статус ордера {order_id} обновлён на '{status}'."
                )
            except StockOrder.DoesNotExist:
                logger.error(
                    f"Ордер с ID {order_id} не найден в базе данных."
                )
            except Exception as e:
                logger.error(
                    f"Ошибка при обновлении ордера {order_id}: {e}"
                )

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON: {e}")
        except Exception as e:
            logger.error(f"Ошибка при обработке данных события: {e}")

    def listen_events(self, url):
        try:
            client = self.connect(url)
            logger.info("Успешно подключен к SSE")
            for event in client:
                if event.data:
                    self.process_event(event.data)
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            logger.info("Попытка восстановить соединение...")
