import json
import os

from rest_framework import serializers
from django.http import FileResponse, HttpResponse
import zipfile, io

from rest_framework.renderers import JSONRenderer

from api.views import person_l
from career.models import Career_data, Career_structure, Persons, Person_photo
from django.conf import settings


# i = open('E:\\dev\\career-backend\\media\\img\\none.jpg', 'rb').read()

# zf = zipfile.ZipFile(o, mode='w')


# zf.writestr('id_card\\none.jpg', i)
# zf.close()
# o.seek(0)
# response = HttpResponse(o.read())
# o.close()
# response['Content-Type'] = 'application/octet-stream'
# response['Content-Disposition'] = "attachment; filename=\"picture.zip\""
#
# with zipfile.ZipFile('Python.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
#     zipf.writestr('E:\\dev\\career-backend\\media\\', i)
#     zipf.close()
# def get_list_image():

class MapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Career_structure
        fields = ['id_card_successor',
                  'name',
                  'company',
                  'type_map',
                  'jdata_org_structure',
                  'jdata_org_successor',
                  'jdata_card_changes',
                  'jdata_card_draft',
                  'jdata_card_default',
                  'draft',
                  'jdata_persons',
                  'jdata_persons_photos'
                  ]

    def create(self, validated_data):
        return Career_structure.objects.create(**validated_data)

def map_download_v2(id=None):
    id_n = id.split('_')[0]
    map_object = Career_structure.objects.get(pk=int(id_n))
    map_serializer = MapSerializer(map_object)
    jdata = JSONRenderer().render(map_serializer.data)
    json_map_data = map_object.jdata_org_structure
    json_map_data_successor = map_object.jdata_org_successor
    jdata_map_persons_photos = map_object.jdata_persons_photos
    org_name = map_object.company

    persons_list, p_list, p_list_kvd = person_l(orgstr=json_map_data, orgsuc=json_map_data_successor, org_name=org_name)
    if map_object.jdata_persons is not None:
        p_list = map_object.jdata_persons
    o = io.BytesIO()

    with zipfile.ZipFile(o, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('map_data.json', jdata)
        zipf.writestr('map_data_person.json', json.dumps(p_list))
        # zipf.writestr('init.json', json.dumps(init))
        for id_pers in persons_list:
            try:
                pers = Person_photo.objects.get(idperson=id_pers)
                img = str(os.path.join(settings.MEDIA_ROOT, pers.img.name))
                zipf.write(img, id_pers+'.' + pers.img.name.split('.')[-1])
                if jdata_map_persons_photos is not None:
                    zipf.write(jdata_map_persons_photos[id_pers], id_pers + '.' + pers.img.name.split('.')[-1])
            except:
                try:
                    if jdata_map_persons_photos is not None:
                        zipf.write(jdata_map_persons_photos[id_pers], id_pers + '.' + jdata_map_persons_photos[id_pers].split('.')[-1])
                except:
                    pass
        zipf.close()
    response = HttpResponse(o.getvalue(), content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="map.zip"'
    return response

def map_download(id=None):
    # Возвращаем zip файл
    map_object = Career_structure.objects.get(pk=int(id))
    json_map_data = map_object.jdata_org_structure
    json_map_data_change = map_object.jdata_card_changes
    json_map_data_successor = map_object.jdata_org_successor
    jdata_map_persons_photos = map_object.jdata_persons_photos
    org_name = map_object.company
    map_name = map_object.name
    if json_map_data_change == None:
        json_map_data_change = []
    if json_map_data_successor == None:
        json_map_data_successor = []
    persons_list, p_list, p_list_kvd = person_l(orgstr=json_map_data, orgsuc=json_map_data_successor, org_name=org_name)
    if map_object.jdata_persons is not None:
        p_list = map_object.jdata_persons

    o = io.BytesIO()
    init = {'org_name': org_name, 'map_name':map_name, 'persons': persons_list}

    with zipfile.ZipFile(o, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('map_data.json', json.dumps(json_map_data))
        zipf.writestr('map_data_change.json', json.dumps(json_map_data_change))
        zipf.writestr('map_data_successor.json', json.dumps(json_map_data_successor))
        zipf.writestr('map_data_person.json', json.dumps(p_list))
        zipf.writestr('init.json', json.dumps(init))
        for id_pers in persons_list:
            try:
                pers = Person_photo.objects.get(idperson=id_pers)
                img = str(os.path.join(settings.MEDIA_ROOT, pers.img.name))
                zipf.write(img, id_pers+'.' + pers.img.name.split('.')[-1])
                if jdata_map_persons_photos is not None:
                    zipf.write(jdata_map_persons_photos[id_pers], id_pers + '.' + pers.img.name.split('.')[-1])
            except:
                try:
                    if jdata_map_persons_photos is not None:
                        zipf.write(jdata_map_persons_photos[id_pers], id_pers + '.' + jdata_map_persons_photos[id_pers].split('.')[-1])
                except:
                    pass
        zipf.close()
    response = HttpResponse(o.getvalue(), content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="map.zip"'
    return response
    # return response
