from django.db import models
from django.contrib.postgres.fields import ArrayField
import uuid


class Order(models.Model):
    itemsInOrder = ArrayField(models.UUIDField(), null=True, blank=True)
    billing = models.UUIDField(null=True, blank=True)
    isClosed = models.BooleanField(default=False, blank=True)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return f'{self.billing}, uuid: {self.uuid}, isClosed: {self.isClosed}'
