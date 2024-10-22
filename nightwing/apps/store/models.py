from django.db import models
from django.conf import settings


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name


class Credit(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    money = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"<{type(self).__name__}: {self.user.username}, ${self.money}>"

    @classmethod
    def get_credit(cls, user):
        return cls.objects.get_or_create(user=user)[0]
