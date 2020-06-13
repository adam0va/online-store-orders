from rest_framework import serializers
from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['itemsInOrder', 'billing', 'isClosed', 'uuid']

    def create(self, validated_data):
        new = Order(**validated_data)
        new.save()
        return new