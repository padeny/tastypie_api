from django.db import models
from django.contrib.auth.models import User


class Author(models.Model):
    name = models.CharField(max_length=128)
    avatar = models.FileField(upload_to='test/avatars', null=True, blank=True)


class Article(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Entry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=128)
    slug = models.CharField(max_length=128)
    created = models.DateTimeField()
    # ImageField need Pillow
    image = models.FileField(upload_to='test/images', null=True, blank=True)
