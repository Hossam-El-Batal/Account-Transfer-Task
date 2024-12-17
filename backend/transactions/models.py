from django.db import models


class Account(models.Model):
    id = models.UUIDField(primary_key=True, null=False)
    name = models.CharField(max_length=255)
    balance = models.FloatField()

    def __str__(self):
        return f"{self.id} ({self.name})"