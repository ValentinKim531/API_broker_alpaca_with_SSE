from django.db import models


class StockOrder(models.Model):
    SIDE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
        ('buy_minus_sell_plus', 'Buy Minus Sell Plus'),
        ('sell_short', 'Sell Short'),
        ('sell_short_exempt', 'Sell Short Exempt'),
        ('undisclosed', 'Undisclosed'),
        ('cross', 'Cross'),
        ('cross_short', 'Cross Short'),
    ]
    TYPE_CHOICES = [
        ('market', 'Market'),
        ('limit', 'Limit'),
        ('stop', 'Stop'),
        ('stop_limit', 'Stop Limit'),
    ]
    TIME_IN_FORCE_CHOICES = [
        ('day', 'Day'),
        ('gtc', 'Good Till Cancelled'),
        ('opg', 'At the Opening'),
        ('cls', 'At the Close'),
    ]

    id_order = models.CharField(
        max_length=50, unique=True, null=True, blank=True
    )
    client_order_id = models.CharField(
        max_length=255, null=True, blank=True
    )
    symbol = models.CharField(max_length=10)
    qty = models.DecimalField(
        max_digits=15, decimal_places=6
    )
    side = models.CharField(
        max_length=20, choices=SIDE_CHOICES
    )
    type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default='market'
    )
    time_in_force = models.CharField(
        max_length=10, choices=TIME_IN_FORCE_CHOICES, default='day'
    )
    status = models.CharField(max_length=20)
    filled_qty = models.DecimalField(
        max_digits=15, decimal_places=6, default=0
    )
    filled_avg_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    filled_at = models.DateTimeField(null=True, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    asset_class = models.CharField(max_length=20, null=True, blank=True)
    extended_hours = models.BooleanField(default=False)
    commission = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    source = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Order {self.id_order} for {self.symbol}"

    class Meta:
        verbose_name = 'Stock order'
        verbose_name_plural = 'Stock orders'
        ordering = ['-created_at']
        db_table = 'Stock orders'
