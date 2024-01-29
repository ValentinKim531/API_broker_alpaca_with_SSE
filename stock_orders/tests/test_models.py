import pytest
from django.utils import timezone
from decimal import Decimal
from stock_orders.models import StockOrder


@pytest.fixture
def stock_order():
    # Создаем экземпляр модели StockOrder для использования в тестах
    return StockOrder(
        id_order="TestOrder123",
        client_order_id="Client123",
        symbol="AAPL",
        qty=Decimal("100.000000"),
        side="buy",
        type="market",
        time_in_force="day",
        status="pending",
        filled_qty=Decimal("0.000000"),
        created_at=timezone.now(),
        updated_at=timezone.now(),
        asset_class="equity"
    )

def test_stock_order_creation(stock_order):
    # Проверяем, что экземпляр модели создается с правильными атрибутами
    assert stock_order.id_order == "TestOrder123"
    assert stock_order.client_order_id == "Client123"
    assert stock_order.symbol == "AAPL"
    assert stock_order.qty == Decimal("100.000000")
    assert stock_order.side == "buy"
    assert stock_order.type == "market"
    assert stock_order.time_in_force == "day"
    assert stock_order.status == "pending"
    assert stock_order.filled_qty == Decimal("0.000000")
    assert isinstance(stock_order.created_at, timezone.datetime)
    assert isinstance(stock_order.updated_at, timezone.datetime)
    assert stock_order.asset_class == "equity"

def test_stock_order_str(stock_order):
    # Проверяем, что метод __str__ возвращает ожидаемое строковое представление
    assert str(stock_order) == f"Order TestOrder123 for AAPL"



@pytest.mark.django_db
def test_stock_order_save_to_db():
    # Создаем и сохраняем экземпляр модели в базу данных
    stock_order = StockOrder(
        id_order="TestOrderDB",
        symbol="TSLA",
        qty=Decimal("50.000000"),
        side="sell",
        status="executed"
    )
    stock_order.save()

    # Извлекаем экземпляр из базы данных и проверяем его атрибуты
    retrieved_order = StockOrder.objects.get(id_order="TestOrderDB")
    assert retrieved_order.symbol == "TSLA"
    assert retrieved_order.qty == Decimal("50.000000")
    assert retrieved_order.side == "sell"
    assert retrieved_order.status == "executed"

@pytest.mark.django_db
def test_stock_order_update_db(stock_order):
    # Сохраняем экземпляр в базу данных, а затем обновляем его
    stock_order.save()
    StockOrder.objects.filter(id_order=stock_order.id_order).update(status="completed")
    updated_order = StockOrder.objects.get(id_order=stock_order.id_order)
    assert updated_order.status == "completed"

@pytest.mark.django_db
def test_stock_order_delete_from_db(stock_order):
    # Сохраняем экземпляр в базу данных, а затем удаляем его
    stock_order.save()
    stock_order_id = stock_order.id_order
    stock_order.delete()
    with pytest.raises(StockOrder.DoesNotExist):
        StockOrder.objects.get(id_order=stock_order_id)
