import base64
import requests
from rest_framework import generics, status
from rest_framework.response import Response
from django.conf import settings
from drf_spectacular.utils import extend_schema

from .models import StockOrder
from .serializers import CreateOrderSerializer, StockOrderListSerializer
from datetime import datetime
import pytz


def get_auth_headers():
    auth_value = base64.b64encode(
        f"{settings.BROKER_API_KEY}:{settings.BROKER_SECRET_KEY}".encode()
    ).decode()
    headers = {
        "accept": "application/json",
        "authorization": f"Basic {auth_value}"
    }
    return headers


def convert_iso8601_to_datetime(iso8601_str):
    iso8601_str = iso8601_str.split('.')[0]
    return datetime.strptime(iso8601_str, "%Y-%m-%dT%H:%M:%S")


class CreateOrderView(generics.CreateAPIView):
    serializer_class = CreateOrderSerializer

    @extend_schema(
        tags=['Create orders'],
        request=CreateOrderSerializer,
        responses={status.HTTP_201_CREATED: CreateOrderSerializer}
    )
    def post(self, request, *args, **kwargs):
        headers = get_auth_headers()
        try:
            response = requests.post(
                f"https://broker-api.sandbox.alpaca.markets/"
                f"v1/trading/accounts/{settings.BROKER_ID}/orders",
                headers=headers,
                json=request.data
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": f"Не удалось отправить запрос в API: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:
            order_data = response.json()
        except ValueError as e:
            return Response(
                {"error": f"Не удалось проанализировать ответ API: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:
            order_data['created_at'] = (
                datetime.fromisoformat(
                    order_data['created_at']).replace(tzinfo=pytz.UTC)
            )
            order_data['updated_at'] = (
                datetime.fromisoformat(
                    order_data['updated_at']).replace(tzinfo=pytz.UTC)
            )
            valid_args = {
                key.name: order_data[key.name]
                for key in StockOrder._meta.get_fields()
                if key.name in order_data
            }
            valid_args['id_order'] = valid_args.pop('id')
            order = StockOrder(**valid_args)
            order.save()
        except Exception as e:
            return Response(
                {"error": f"Failed to save order: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StockOrderListView(generics.ListAPIView):
    serializer_class = StockOrderListSerializer

    @extend_schema(
        tags=['List of orders'],
        responses={status.HTTP_200_OK: StockOrderListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        try:
            orders = StockOrder.objects.all()
            serializer = self.get_serializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Не удалось получить ордера: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeleteOrderView(generics.DestroyAPIView):

    @extend_schema(
        tags=['Cancel orders']
    )
    def delete(self, request, *args, **kwargs):
        headers = get_auth_headers()
        id_order = self.kwargs['id_order']
        try:
            order = StockOrder.objects.filter(id_order=id_order).first()
            if order is not None:
                order.delete()
                response = requests.delete(
                    f"https://broker-api.sandbox.alpaca.markets/"
                    f"v1/trading/accounts/{settings.BROKER_ID}/"
                    f"orders/{id_order}",
                    headers=headers
                )
                response.raise_for_status()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"error": "Ордер не найден"},
                    status=status.HTTP_404_NOT_FOUND
                )
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": f"Не удалось отправить запрос в API: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {"error": f"Не удалось отменить ордер: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
