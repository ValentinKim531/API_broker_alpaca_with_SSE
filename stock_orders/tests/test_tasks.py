import pytest
from unittest.mock import patch
from celery.contrib.testing.worker import start_worker
from backend.celery import app
from stock_orders.tasks import listen_to_alpaca_sse


# Фикстуры Celery
@pytest.fixture(scope="module")
def celery_app():
    app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
        broker_url="memory://",
        backend="cache+memory://",
    )
    return app


@pytest.fixture(scope="module")
def celery_worker(celery_app):
    with start_worker(celery_app, perform_ping_check=False) as worker:
        yield worker


# Тесты
@pytest.mark.django_db
@patch("stock_orders.tasks.AlpacaSSEService")
@patch("stock_orders.tasks.logger")
def test_listen_to_alpaca_sse_integration(
    mock_logger, mock_alpaca_service, celery_app, celery_worker
):
    mock_alpaca_service_instance = mock_alpaca_service.return_value
    mock_alpaca_service_instance.listen_events.return_value = None

    listen_to_alpaca_sse.delay()

    mock_alpaca_service_instance.listen_events.assert_called_once()
    mock_logger.info.assert_any_call("Задача SSE запущена")
    mock_logger.info.assert_any_call("Подключение к SSE-серверу успешно")

    mock_alpaca_service_instance.listen_events.side_effect = Exception(
        "Test error"
    )
    listen_to_alpaca_sse.delay()
    mock_logger.error.assert_called_with(
        "Ошибка при подключении к SSE-серверу: Test error"
    )


@patch("stock_orders.tasks.AlpacaSSEService")
@patch("stock_orders.tasks.logger")
def test_listen_to_alpaca_sse_success(
    mock_logger, mock_alpaca_service, celery_app
):
    mock_alpaca_service_instance = mock_alpaca_service.return_value
    mock_alpaca_service_instance.listen_events.return_value = None

    listen_to_alpaca_sse()

    mock_alpaca_service_instance.listen_events.assert_called_once()
    mock_logger.info.assert_any_call("Задача SSE запущена")
    mock_logger.info.assert_any_call("Подключение к SSE-серверу успешно")


@patch("stock_orders.tasks.AlpacaSSEService")
@patch("stock_orders.tasks.logger")
def test_listen_to_alpaca_sse_failure(
    mock_logger, mock_alpaca_service, celery_app
):
    mock_alpaca_service_instance = mock_alpaca_service.return_value
    mock_alpaca_service_instance.listen_events.side_effect = Exception(
        "Test error"
    )

    listen_to_alpaca_sse()

    mock_alpaca_service_instance.listen_events.assert_called_once()
    mock_logger.error.assert_called_with(
        "Ошибка при подключении к SSE-серверу: Test error"
    )
