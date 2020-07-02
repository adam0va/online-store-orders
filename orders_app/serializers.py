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

    def update(self, instance: Order, validated_data):
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance