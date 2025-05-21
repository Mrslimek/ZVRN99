from django.db import models


class ReceivedDataORM(models.Model):
    name = models.CharField(max_length=49)
    date = models.DateTimeField()