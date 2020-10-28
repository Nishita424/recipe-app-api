from django.db import models
from django.conf import settings


class Tag(models.Model):
    """Tag to be used for a recipe"""
    name = models.CharField(max_length=255)
    # user = models.ForeignKey('User', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, # Best practice
                             on_delete=models.CASCADE)
    objects = models.Manager()

    def __str__(self):
        return self.name
