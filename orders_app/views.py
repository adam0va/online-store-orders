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
        print('12345')
        orders = Order.objects.all()
        serialized_orders = [OrderSerializer(order).data for order in orders]
        for order in serialized_orders:
            # добавляем к ним информацию о биллинге, если она есть
            if order['billing']:
                billing_response, billing_status = self.BILLING_REQUESTER.get_billing(uuid=order['billing'])
                print(billing_response)
                if billing_status == 200:
                    billing_data = self.BILLING_REQUESTER.get_data_from_response(billing_response)
                    order['billing'] = billing_data[0]
            if order['itemsInOrder']:
                for i in range(len(order['itemsInOrder'])):
                    item_response, item_status = self.ITEM_REQUESTER.get_item(uuid=order['itemsInOrder'][i])
                    if item_status == 200:
                        order_data = self.BILLING_REQUESTER.get_data_from_response(item_response)
                        order['itemsInOrder'][i] = order_data[0]

        return Response(serialized_orders, status=status.HTTP_200_OK)

    '''
    def post(self, request):
        data = request.data
        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    '''
    def post(self, request):
        # при создании заказа сразу создается биллинг
        data = request.data
        serializer = OrderSerializer(data=data)
        billing_response, billing_status_code = self.BILLING_REQUESTER.post_billing()
        if billing_status_code != 201:
            return Response(status=billing_status_code)
        billing_data = self.BILLING_REQUESTER.get_data_from_response(billing_response)
        print(billing_data)
        billing_uuid = billing_data['uuid']
        order = Order.objects.create(billing=billing_uuid)
        order_json = OrderSerializer(instance=order).data
        return Response(order_json, status=status.HTTP_201_CREATED)

        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class NotDetailedOrdersList(APIView):
    def get(self, request):
        # GET-запрос на заказы без информации о биллинге и покупках
        orders = Order.objects.all()
        serialized_orders = [OrderSerializer(order).data for order in orders]

        return Response(serialized_orders, status=status.HTTP_200_OK)


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
            billing_response, billing_status = self.BILLING_REQUESTER.get_billing(uuid=serialized.data['billing'])
            if billing_status == 200:
                billing_data = self.BILLING_REQUESTER.get_data_from_response(billing_response)
                data_to_change['billing'] = billing_data
        if data_to_change['itemsInOrder']:
            # получаем список товаров
            for i in range(len(data_to_change['itemsInOrder'])):
                item_response, item_status = self.ITEM_REQUESTER.get_item(uuid=data_to_change['itemsInOrder'][i])
                if item_status == 200:
                    item_data = self.BILLING_REQUESTER.get_data_from_response(item_response)
                    data_to_change['itemsInOrder'][i] = item_data

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


class OrderWithoutDetail(APIView):
    def get(self, request, uuid):
        # GET-запрос с uuid
        try:
            order = Order.objects.get(pk=uuid)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serialized = OrderSerializer(order)

        return Response(serialized.data, status=status.HTTP_200_OK)