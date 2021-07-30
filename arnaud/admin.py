from django.contrib import admin

# Register your models here.
from arnaud.models import Image, Comment, Person

admin.site.register(Image)
admin.site.register(Comment)
admin.site.register(Person)