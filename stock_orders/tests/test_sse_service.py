import pytest
from unittest.mock import patch, MagicMock
from django.conf import settings
from stock_orders.sse_service import AlpacaSSEService
from stock_orders.models import StockOrder
import base64


@pytest.fixture
def stock_order():
    return StockOrder.objects.create(
        id_order="test_order_id",
        symbol="AAPL",
        qty=10,
        side="buy",
        status="pending",
    )


@pytest.mark.django_db
@patch("stock_orders.sse_service.SSEClient")
def test_process_event_updates_order_status(mock_sse_client, stock_order, db):
    mock_event = MagicMock()
    mock_event.data = (
        '{"order": {"id": "test_order_id", "status": "completed"}}'
    )

    sse_service = AlpacaSSEService()
    sse_service.process_event(mock_event.data)

    stock_order.refresh_from_db()
    assert stock_order.status == "completed"


@patch("stock_orders.sse_service.SSEClient")
def test_listen_events_handles_exceptions(mock_sse_client, db):
    mock_sse_client.side_effect = Exception("Ошибка подключения")

    sse_service = AlpacaSSEService()

    with patch("stock_orders.sse_service.logger") as mock_logger:
        sse_service.listen_events("mock_url")
        mock_logger.error.assert_called_with("Ошибка: Ошибка подключения")
        mock_logger.info.assert_called_with(
            "Попытка восстановить соединение..."
        )


@pytest.mark.django_db
@patch("stock_orders.sse_service.SSEClient")
def test_process_event_with_invalid_json(mock_sse_client, db):
    mock_event = MagicMock()
    mock_event.data = "Невалидный JSON"

    sse_service = AlpacaSSEService()
    with patch("stock_orders.sse_service.logger") as mock_logger:
        sse_service.process_event(mock_event.data)
        mock_logger.error.assert_called_with(
            "Ошибка декодирования JSON: "
            "Expecting value: line 1 column 1 (char 0)"
        )


@pytest.mark.django_db
@patch("stock_orders.sse_service.SSEClient")
def test_process_event_without_order_id(mock_sse_client, db):
    mock_event = MagicMock()
    mock_event.data = '{"order": {"status": "completed"}}'

    sse_service = AlpacaSSEService()
    with patch("stock_orders.sse_service.logger") as mock_logger:
        sse_service.process_event(mock_event.data)
        mock_logger.error.assert_called_with(
            "Отсутствует ID ордера в данных: "
            "{'order': {'status': 'completed'}}"
        )


@pytest.mark.django_db
@patch("stock_orders.sse_service.SSEClient")
def test_process_event_for_nonexistent_order(mock_sse_client, stock_order, db):
    mock_event = MagicMock()
    mock_event.data = (
        '{"order": {"id": "nonexistent_order_id", "status": "completed"}}'
    )

    sse_service = AlpacaSSEService()
    with patch("stock_orders.sse_service.logger") as mock_logger:
        sse_service.process_event(mock_event.data)
        mock_logger.error.assert_called_with(
            "Ордер с ID nonexistent_order_id не найден в базе данных."
        )


@pytest.mark.django_db
@patch("stock_orders.sse_service.SSEClient")
def test_process_event_without_order_status(mock_sse_client, stock_order, db):
    mock_event = MagicMock()
    mock_event.data = '{"order": {"id": "test_order_id"}}'

    sse_service = AlpacaSSEService()
    with patch("stock_orders.sse_service.logger") as mock_logger:
        sse_service.process_event(mock_event.data)
        mock_logger.error.assert_called_with(
            "Отсутствует статус в ордерах: {'id': 'test_order_id'}"
        )


def test_get_credentials():
    sse_service = AlpacaSSEService()
    expected_credentials = base64.b64encode(
        f"{settings.BROKER_API_KEY}:{settings.BROKER_SECRET_KEY}".encode(
            "utf-8"
        )
    ).decode("utf-8")
    assert sse_service.get_credentials() == expected_credentials


@patch("stock_orders.sse_service.SSEClient")
def test_connect(mock_sse_client):
    url = "mock_url"
    sse_service = AlpacaSSEService()
    sse_service.connect(url)
    mock_sse_client.assert_called_once()
    args, kwargs = mock_sse_client.call_args
    assert args[0] == url
    assert "Authorization" in kwargs["headers"]


@patch("stock_orders.sse_service.SSEClient")
def test_listen_events_with_multiple_events(mock_sse_client, db):
    mock_client_instance = mock_sse_client.return_value
    mock_client_instance.__iter__.return_value = [
        MagicMock(
            data='{"order": {"id": "test_order_id_1", "status": "completed"}}'
        ),
        MagicMock(
            data='{"order": {"id": "test_order_id_2", "status": "cancelled"}}'
        ),
    ]

    sse_service = AlpacaSSEService()
    with patch("stock_orders.sse_service.logger") as mock_logger:
        sse_service.listen_events("mock_url")


@patch("stock_orders.sse_service.SSEClient")
def test_connect_sets_correct_headers(mock_sse_client):
    url = "mock_url"
    sse_service = AlpacaSSEService()
    sse_service.connect(url)
    mock_sse_client.assert_called_once()
    _, kwargs = mock_sse_client.call_args
    headers = kwargs["headers"]
    assert "Accept" in headers and headers["Accept"] == "text/event-stream"
    assert "Authorization" in headers
    assert headers["Authorization"].startswith("Basic ")
