import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient
from stock_orders.models import StockOrder
from rest_framework import status
import requests_mock

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def stock_order_data():
    """Тестовый ордер - экземпляр StockOrder"""
    return {
        'symbol': 'AAPL',
        'qty': 10,
        'side': 'buy',
        'type': 'market',
        'time_in_force': 'day'
    }


@pytest.fixture
def stock_order(db):
    """Тестовый ордер - экземпляр StockOrder"""
    return StockOrder.objects.create(
        id_order='a75bf79b-df8b-4572-813a-2380320081c4',
        symbol="AAPL",
        qty="10.00",
        side="buy",
        type="market",
        time_in_force="day",
        status="pending"
    )


@pytest.mark.django_db
def test_create_order_view(api_client, stock_order_data):
    url = reverse('create-order')
    response = api_client.post(url, stock_order_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert StockOrder.objects.count() == 1


@pytest.mark.django_db
def test_stock_order_list_view(api_client, stock_order):
    url = reverse('order-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1


@pytest.mark.django_db
def test_delete_order_view(api_client, stock_order):
    with requests_mock.Mocker() as m:
        # Настраиваем мок для запроса на удаление ордера у внешнего сервиса
        m.delete(f"https://broker-api.sandbox.alpaca.markets/v1/trading/accounts/{settings.BROKER_ID}/orders/{stock_order.id_order}", status_code=200)

        url = reverse('delete-order', kwargs={'id_order': stock_order.id_order})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert StockOrder.objects.count() == 0
