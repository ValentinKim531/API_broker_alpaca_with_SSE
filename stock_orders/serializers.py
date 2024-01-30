from rest_framework import serializers
from .models import StockOrder


class CreateOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockOrder
        fields = (
            'symbol',
            'qty',
            'side',
            'type',
            'time_in_force'
        )

    def validate_qty(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Кол-во не должно быть меньше или равно 0"
            )
        return value


class StockOrderListSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockOrder
        fields = (
            'id_order',
            'client_order_id',
            'symbol',
            'qty',
            'side',
            'type',
            'time_in_force',
            'status',
            'filled_qty',
            'filled_avg_price',
            'created_at',
            'updated_at',
            'submitted_at',
            'filled_at',
            'expired_at',
            'canceled_at',
            'failed_at',
            'asset_class',
            'extended_hours',
            'commission',
            'source'
        )
