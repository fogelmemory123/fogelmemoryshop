# serializers.py
from rest_framework import serializers
from .models import Product, Category, Cart, CartItem, Order, OrderItem,OrderHistory

# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'image',
            'image_url',
            'price',
            'stock',
            'category',
            'created_at',
            'updated_at'
        ]

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']

# CartItem Serializer
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # Include product details

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'added_at']

# Cart Serializer
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)  # Include all cart items

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at']

# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'created_at']

# OrderItem Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # Include product details

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'price']


class OrderHistorySerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")  # פורמט קריא יותר

    class Meta:
        model = OrderHistory
        fields = ['id', 'transaction_id', 'total_amount', 'payer_email',
                  'payer_name', 'created_at', 'status', 'items']
