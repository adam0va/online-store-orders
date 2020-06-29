from rest_framework import status
from rest_framework.views import Response, Request, APIView
from orders_app.models import Order
from orders_app.serializers import OrderSerializer
from orders_app.requesters.billing_requester import BillingRequester
from orders_app.requesters.items_requester import ItemsRequester

'''
8002 порт
Заказ включает в себя список товаров, которые в него входят,
а так же биллинг, относящийся к нему.
Таким образом, при GET запросе, необходимо обращаться
также к сервисам товаров и биллинга.
При PATCH, POST, DELETE запросах обращение к сервису товаров не требуется, 
поскольку они существуют независимо от того, находятся ли они в каком-то
заказе.
При DELETE запросе биллинг, соответствующий заказу, должен удаляться.
Остальные запросы на него не влияют (но, может быть, надо сделать так,
чтобы биллинг создавался вместе с заказом)
'''

class OrderList(APIView):
    BILLING_REQUESTER = BillingRequester()
    ITEM_REQUESTER = ItemsRequester()

    def get(self, request):
        # GET-запрос без uuid
        orders = Order.objects.all()
        serialized_orders = [OrderSerializer(order).data for order in orders]
        for order in serialized_orders:
            # добавляем к ним информацию о биллинге, если она есть
            if order['billing']:
                billing_response = self.BILLING_REQUESTER.get_billing(uuid=order['billing'])
                if not billing_response == self.ITEM_REQUESTER.BASE_HTTP_ERROR:
                    order['billing'] = billing_response[0].json()
            if order['itemsInOrder']:
                for i in range(len(order['itemsInOrder'])):
                    item_response = self.ITEM_REQUESTER.get_item(uuid=order['itemsInOrder'][i])
                    if not billing_response == self.ITEM_REQUESTER.BASE_HTTP_ERROR:
                        order['itemsInOrder'][i] = item_response[0].json()

        return Response(serialized_orders, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetail(APIView):
    BILLING_REQUESTER = BillingRequester()
    ITEM_REQUESTER = ItemsRequester()

    def get(self, request, uuid):
        # GET-запрос с uuid
        try:
            order = Order.objects.get(pk=uuid)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serialized = OrderSerializer(order)
        data_to_change = serialized.data
        if serialized.data['billing']:
            billing_response = self.BILLING_REQUESTER.get_billing(uuid=serialized.data['billing'])
            if not billing_response == self.ITEM_REQUESTER.BASE_HTTP_ERROR:
                data_to_change['billing'] = billing_response[0].json()
        if data_to_change['itemsInOrder']:
            # получаем список товаров
            for i in range(len(data_to_change['itemsInOrder'])):
                item_response = self.ITEM_REQUESTER.get_item(uuid=data_to_change['itemsInOrder'][i])
                if not billing_response == self.ITEM_REQUESTER.BASE_HTTP_ERROR:
                    data_to_change['itemsInOrder'][i] = item_response[0].json()

        return Response(data_to_change, status=status.HTTP_200_OK)

    def patch(self, request, uuid):
        try:
            item = Order.objects.get(pk=uuid)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(instance=item, data=request.data)
        if serializer.is_valid():
            # чтобы выводить информацию об измененном заказе подробной информацией
            # о биллинге и товарах, добавить код здесь
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uuid):
        try:
            order = Order.objects.get(uuid=uuid)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        billing_response, billing_status_code = self.BILLING_REQUESTER.delete_billing(uuid=order.billing)
        if billing_status_code == 204:
            order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)