from django.db import models
from django.contrib.auth.models import User


class Entry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=128)
    slug = models.CharField(max_length=128)
    created = models.DateTimeField()
    # ImageField need Pillow
    image = models.FileField(upload_to='test/images', null=True, blank=True)
