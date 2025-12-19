from django.db import models

# Create your models here.

class UserDetail(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    age = models.IntegerField()
    message = models.TextField(blank=True)

    def __str__(self):
        return self.name
