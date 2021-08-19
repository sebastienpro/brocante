import functools
import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect

# Create your views here.

from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt

from arnaud.models import Image, Person, Interested, Comment
from PIL import Image as PilImage, ExifTags


def generate_thumbnail(image_path):
    image = PilImage.open(image_path)
    image_name = os.path.basename(image_path)
    MAX_SIZE = (200, 200)

    try:
        orientation_item = None
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                orientation_item = orientation
        exif = dict(image._getexif().items())

        if exif[orientation_item] == 3:
            image = image.rotate(180, expand=True)
        elif exif[orientation_item] == 6:
            image = image.rotate(270, expand=True)
        elif exif[orientation_item] == 8:
            image = image.rotate(90, expand=True)
    except:
        pass

    image.thumbnail(MAX_SIZE)
    image.save(os.path.join(settings.MEDIA_ROOT,'thumbnail',image_name))


def get_user_from_cookie(a_view):
    @functools.wraps(a_view)
    def _wrapped_view(request, *args, **kwargs):
        try:
            user_name = request.COOKIES['nom']
            kwargs['user'] = Person.objects.get(name=user_name)
        except (Person.DoesNotExist, KeyError):
            response = HttpResponse(render(request, "authent.html"))
            response.delete_cookie('nom')
            return response

        return a_view(request, *args, **kwargs)

    return _wrapped_view



@csrf_exempt
def index(request):
    response = HttpResponse("Hello, world. You're at the polls index.")
    if request.method == 'POST':
        password = request.POST['password']
        nom = request.POST['nom']
        if password != 'ceret':
            return HttpResponse("Mauvais mot de passe")
        else:
            images = Image.objects.all()
            response = HttpResponse(
                render(request, "liste.html", context={'nom': nom, 'images': images})
            )
            response.set_cookie('nom', nom)
            if not Person.objects.filter(name=nom).exists():
                Person.objects.create(name=nom)
    else:
        if 'nom' not in request.COOKIES:
            response =  HttpResponse(render(request, "authent.html"))
        else:
            nom = request.COOKIES['nom']
            images = Image.objects.all()
            response = HttpResponse(
                render(request, "liste.html", context={'nom': nom, 'images': images})
            )
    return response

@get_user_from_cookie
@csrf_exempt
def detail(request, image_id, user):
    image = Image.objects.get(id=image_id)
    is_interesting = image.persons.filter(id=user.pk).exists()

    if request.method == 'POST':
        if request.POST.get('action') == 'interesting':
            is_interesting = not is_interesting
            if is_interesting:
                image.persons.add(user)
            else:
                image.persons.remove(user)
        elif request.POST.get('action') == 'comment':
            comment = request.POST['comment']
            Comment.objects.create(text=comment, person=user, image=image)
        return redirect('detail', image_id=image_id)

    elif 'page' in request.GET:
        kind = request.GET['page']
        if kind == 'next':
            images = Image.objects.filter(id__gt=image_id).order_by('id')
        elif kind == 'previous':
            images = Image.objects.filter(id__lt=image_id).order_by('-id')
        if images.exists():
            return redirect('detail', image_id=images[0].pk)
        else:
            if kind == 'next':
                return redirect('detail', image_id=Image.objects.first().pk)
            else:
                return redirect('detail', image_id=Image.objects.last().pk)

    comments = Comment.objects.filter(image=image)
    return HttpResponse(
        render(
            request,
            "detail.html",
            context={
                'image': image,
                'is_interesting': is_interesting,
                'interested': Interested.objects.filter(image=image),
                'is_reserved': Interested.objects.filter(image=image).exclude(person=user).exists(),
                'comments': comments
            }
        )
    )


@csrf_exempt
def add(request):
    send  = False
    if request.method == 'POST' and request.FILES['photo']:
        photo = request.FILES['photo']
        fs = FileSystemStorage()
        filename = fs.save(photo.name, photo)
        saved_image = Image(image_name=filename)
        saved_image.save()
        generate_thumbnail(fs.path(filename))
        send = True
    return HttpResponse(render(request, 'add.html', context={'send': send}))