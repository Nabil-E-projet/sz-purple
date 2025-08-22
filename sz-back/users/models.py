from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db import transaction
from django.db.models import F

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    credits = models.IntegerField(default=0)
    
    def __str__(self):
        return self.email

    def has_credits(self, amount: int = 1) -> bool:
        try:
            return int(self.credits) >= int(amount)
        except Exception:
            return False

    def try_consume_credits(self, amount: int = 1) -> bool:
        """Atomically consume credits if available; return True if consumed."""
        amount = int(amount)
        if amount <= 0:
            return True
        with transaction.atomic():
            locked = type(self).objects.select_for_update().get(pk=self.pk)
            if locked.credits >= amount:
                type(self).objects.filter(pk=self.pk).update(credits=F('credits') - amount)
                # Refresh current instance
                self.refresh_from_db(fields=['credits'])
                return True
            return False

    def add_credits(self, amount: int) -> None:
        amount = int(amount)
        if amount <= 0:
            return
        type(self).objects.filter(pk=self.pk).update(credits=F('credits') + amount)
        self.refresh_from_db(fields=['credits'])