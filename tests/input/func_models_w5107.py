"""
Check for model field redefinition
"""
from django.db import models


class Category(models.Model):
    """Category"""
    name = models.CharField()
    name = models.CharField()

    def __unicode__(self):
        return self.name
