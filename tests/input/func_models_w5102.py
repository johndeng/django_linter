"""
Check for correct type for money related field
"""
from django.db import models


class Product(models.Model):
    """Product"""
    name = models.CharField(max_length=255)
    price = models.FloatField()

    def __unicode__(self):
        return self.name
