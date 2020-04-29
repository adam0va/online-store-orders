from rest_framework import status
from rest_framework.views import Response, Request, APIView
from orders_app.models import Order
from orders_app.serializers import OrderSerializer
from rest_framework.generics import ListCreateAPIView
#from rest_framework.parsers import MultiPartParser


class ItemList(ListCreateAPIView):
    serializer_class = OrderSerializer
    #parser_classes = (MultiPartParser, )

    def get_queryset(self):
        return Order.objects.all()

    def post(self, request):
        data = request.data
        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ItemDetail(APIView):
    def get(self, request, uuid):
        try:
            reader = Order.objects.get(pk=uuid)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(reader)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, uuid):
        try:
            reader = Order.objects.get(pk=uuid)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(instance=reader, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uuid):
        try:
            reader = Order.objects.get(uuid=uuid)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        reader.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)