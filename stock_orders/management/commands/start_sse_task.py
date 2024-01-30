from django.core.management.base import BaseCommand
from stock_orders.tasks import listen_to_alpaca_sse


class Command(BaseCommand):
    help = 'Starts the SSE listening task'

    def handle(self, *args, **options):
        listen_to_alpaca_sse.delay()
        self.stdout.write(self.style.SUCCESS('Запуск SSE произведен успешно.'))
