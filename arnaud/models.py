from datetime import datetime

from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Image(models.Model):
    image_name = models.CharField(max_length=200)
    persons = models.ManyToManyField(Person, through='Interested')

    def __str__(self):
        return self.image_name

class Interested(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(default=datetime.now())

class Comment(models.Model):
    text = models.TextField()
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    def __str__(self):
        return self.text