import pytest
from django.utils import timezone
from decimal import Decimal
from stock_orders.models import StockOrder
from stock_orders.serializers import (
    CreateOrderSerializer, StockOrderListSerializer)


@pytest.fixture
def stock_order_data():
    """Тестовый ордер - экземпляр StockOrder"""

    return {
        'symbol': 'AAPL',
        'qty': 10.0,
        'side': 'buy',
        'type': 'market',
        'time_in_force': 'day'
    }


@pytest.fixture
def full_stock_order_data():
    """Тестовый ордер - экземпляр StockOrder"""

    return {
        'id_order': 'TestOrder123',
        'client_order_id': 'ClientID123',
        'symbol': 'AAPL',
        'qty': Decimal('10.000000'),
        'side': 'buy',
        'type': 'market',
        'time_in_force': 'day',
        'status': 'pending',
        'filled_qty': Decimal('0.000000'),
        'filled_avg_price': Decimal('150.00'),
        'created_at': timezone.now(),
        'updated_at': timezone.now(),
        'submitted_at': timezone.now(),
        'filled_at': timezone.now(),
        'expired_at': timezone.now(),
        'canceled_at': timezone.now(),
        'failed_at': timezone.now(),
        'asset_class': 'equity',
        'extended_hours': True,
        'commission': Decimal('1.00'),
        'source': 'manual'
    }


@pytest.fixture
def stock_order_instance(stock_order_data):
    return StockOrder.objects.create(**stock_order_data, status='pending')


@pytest.mark.django_db
def test_create_order_serializer_valid(stock_order_data):
    serializer = CreateOrderSerializer(data=stock_order_data)
    assert serializer.is_valid()
    order = serializer.save()
    assert StockOrder.objects.count() == 1
    assert order.symbol == 'AAPL'


@pytest.mark.django_db
def test_create_order_serializer_invalid(stock_order_data):
    invalid_data = stock_order_data.copy()
    invalid_data['qty'] = -10  # Невалидное количество
    serializer = CreateOrderSerializer(data=invalid_data)
    assert not serializer.is_valid()


@pytest.mark.django_db
def test_stock_order_list_serializer_full(full_stock_order_data):
    """Создание экземпляра модели StockOrder с полными данными"""

    stock_order = StockOrder.objects.create(**full_stock_order_data)

    # Сериализация экземпляра модели
    serializer = StockOrderListSerializer(instance=stock_order)
    data = serializer.data

    # Проверка сериализованных данных
    assert data['id_order'] == 'TestOrder123'
    assert data['client_order_id'] == 'ClientID123'
    assert data['symbol'] == 'AAPL'
    assert data['qty'] == '10.000000'
    assert data['side'] == 'buy'
    assert data['type'] == 'market'
    assert data['time_in_force'] == 'day'
    assert data['status'] == 'pending'
    assert data['filled_qty'] == '0.000000'
    assert str(data['filled_avg_price']) == '150.00'
    assert data['asset_class'] == 'equity'
    assert data['extended_hours'] is True
    assert str(data['commission']) == '1.00'
    assert data['source'] == 'manual'

    # Проверка полей даты (пример)
    assert 'created_at' in data
    assert 'updated_at' in data
    assert 'submitted_at' in data
    assert 'filled_at' in data
    assert 'expired_at' in data
    assert 'canceled_at' in data
    assert 'failed_at' in data
