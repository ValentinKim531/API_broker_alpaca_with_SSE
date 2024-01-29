from django.urls import path
from . import views

urlpatterns = [
    path('orders/create/',
         views.CreateOrderView.as_view(),
         name='create-order'
         ),
    path(
        'orders/',
        views.StockOrderListView.as_view(),
        name='order-list'
    ),
    path(
        'orders/<str:id_order>/delete/',
        views.DeleteOrderView.as_view(),
        name='delete-order'
    ),
]
