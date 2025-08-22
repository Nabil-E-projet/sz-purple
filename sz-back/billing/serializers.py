from rest_framework import serializers
from .models import Order, CreditTransaction


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            'id', 'status', 'credits', 'amount_cents', 'currency', 'stripe_session_id', 'created_at'
        )
        read_only_fields = ('id', 'status', 'stripe_session_id', 'created_at')


class CreditTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditTransaction
        fields = ('id', 'type', 'amount', 'description', 'created_at')
        read_only_fields = fields

