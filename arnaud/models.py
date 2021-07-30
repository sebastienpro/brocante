from datetime import datetime

from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=200)

class Image(models.Model):
    image_name = models.CharField(max_length=200)
    persons = models.ManyToManyField(Person, through='Interested')

class Interested(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(default=datetime.now())