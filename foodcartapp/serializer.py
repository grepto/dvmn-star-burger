from rest_framework.serializers import ModelSerializer, ValidationError

from .models import Order, OrderItem


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('id',)

    def validate_products(self, value):
        if not value:
            raise ValidationError("products can't be an empty list")

        return value