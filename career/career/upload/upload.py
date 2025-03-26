from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from career.models import Person_photo, Person_profile, Persons, SPerson
from career.upload.generator_id import id_generate


class MyUploadView(APIView):
    parser_class = (MultiPartParser)

    def post(self, request):
        if 'file' not in request.data:
            raise ParseError("Empty content")

        f = request.data['file']

        # mymodel.my_file_field.save(f.name, f, save=True)
        return Response(status=status.HTTP_201_CREATED)


def photo_load(file_obj):
    filename = file_obj.name.split('.')[0].strip()
    filename = " ".join(filename.split())
    id_ruk = id_generate(filename)
    obj, created = Person_photo.objects.update_or_create(
        idperson=id_ruk,
        defaults={'img': file_obj,
                  'name':filename})
    # print(obj, created)

def photo_load_one(file_obj,id):
    filename = file_obj.name.split('.')[0].strip()
    filename = " ".join(filename.split())
    id_ruk = id
    obj, created = Person_photo.objects.update_or_create(
        idperson=id_ruk,
        defaults={'img': file_obj,
                  'name':filename})

def profile_load_one(file_obj,id):
    filename = file_obj.name.split('.')[0].strip()
    filename = " ".join(filename.split())
    name = filename
    try:
        person = Persons.objects.get(person_id=id)
        name = person.person_name
    except:
        pass

    try:
        person = SPerson.objects.get(uid=id[0:20])
        name = person.name
    except:
        pass

    obj, created = Person_profile.objects.update_or_create(
        idperson=id[0:20],
        defaults={'profile_file': file_obj,
                  'name': name})

def delete_profile_file(id):
    try:
        profile = Person_profile.objects.get(idperson__istartswith=id[0:20])
        profile.profile_file=None
        profile.save()
        # person = Persons.objects.get(person_id=id)
        # person.profile=False
        # person.save()
    except:
        pass