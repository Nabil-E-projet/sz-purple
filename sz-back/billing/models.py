from django.db import models
from django.conf import settings
from django.utils import timezone


class CreditTransaction(models.Model):
    CREDIT_TYPES = [
        ("purchase", "Purchase"),
        ("grant", "Grant"),
        ("consume", "Consume"),
        ("refund", "Refund"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="credit_transactions")
    created_at = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=16, choices=CREDIT_TYPES)
    amount = models.IntegerField()
    description = models.CharField(max_length=255, blank=True, null=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]


class Order(models.Model):
    STATUS_CHOICES = [
        ("created", "Created"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("expired", "Expired"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="created")
    credits = models.IntegerField(default=0)
    amount_cents = models.IntegerField(default=0)
    currency = models.CharField(max_length=8, default="eur")
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

