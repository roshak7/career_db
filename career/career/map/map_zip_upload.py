import os
import zipfile, io
import json
from django.conf import settings

from career.map.map_zip_download import MapSerializer
from career.models import Career_structure

def map_upload_v2(zip_file=None):
    # serializer = PostSerializer(data=data)
    with zipfile.ZipFile(zip_file) as zpf:

        map_data = json.loads(zpf.read('map_data.json').decode('utf-8'))
        # map_data_change = json.loads(zpf.read('map_data_change.json').decode('utf-8'))
        # map_data_person = json.loads(zpf.read('map_data_person.json').decode('utf-8'))
        # map_data_successor = json.loads(zpf.read('map_data_successor.json').decode('utf-8'))
        # init = zpf.read('init.json')

        # init_dict = json.loads(init.decode('utf-8'))
        # car_new = Career_structure(name=map_data['name'])
        # car_new.save()
        # print(car_new.id)

        # cnew, obj = Career_structure.objects.update_or_create(id=car_new.id, defaults=map_data)


            # name=map_data['name'], company=map_data['org_name'],
            #                        type_map = map_data['type_map'],
            #                        jdata_org_structure=map_data['jdata_org_structure'], jdata_org_successor=map_data['jdata_org_successor'],
            #                        jdata_card_changes=map_data['jdata_card_changes'],
            #                        jdata_card_draft=map_data['jdata_card_draft'],
            #                        jdata_card_default=map_data['jdata_card_default'],
            #                        draft=map_data['draft'],
            #                        draft=map_data['draft'],
            #                        draft=map_data['draft'],
            #                        draft=map_data['draft'],




                                   # jdata_persons=map_data_person,
                                   # )
        # car_new.save()

        # id = car_new.id
        serializer = MapSerializer(data=map_data)
        if serializer.is_valid():
            map = serializer.save()
            # map_instance = serializer.save()
            # print(f"Создан объект Post: {map.id}")
        else:
            return 0
        img_files = {}
        car_new = Career_structure.objects.get(id=map.id)
        for f in zpf.namelist():
            if f.split('.')[-1] in ['jpg', 'jpeg', 'png']:
                img_dir = str(os.path.join(settings.MEDIA_ROOT, 'img', str(map.id)))
                zpf.extract(f, img_dir)
                img_files.update({str(f.split('.')[0]): str(os.path.join(img_dir, f))})
        car_new.jdata_persons_photos = img_files
        car_new.save()

    return [map.id, {'report': 'Карта из пакетного файла ZIP загружена'}]
def map_upload(zip_file=None):
    # Возвращаем ID созданной карты

    with zipfile.ZipFile(zip_file) as zpf:

        map_data = json.loads(zpf.read('map_data.json').decode('utf-8'))
        map_data_change = json.loads(zpf.read('map_data_change.json').decode('utf-8'))
        map_data_person = json.loads(zpf.read('map_data_person.json').decode('utf-8'))
        map_data_successor = json.loads(zpf.read('map_data_successor.json').decode('utf-8'))
        init = zpf.read('init.json')

        init_dict = json.loads(init.decode('utf-8'))

        car_new = Career_structure(name=init_dict['map_name'], company=init_dict['org_name'],
                                   jdata_org_structure=map_data, jdata_org_successor=map_data_successor,
                                   jdata_card_changes=map_data_change, jdata_persons=map_data_person,
                                   )
        car_new.save()

        id = car_new.id
        img_files = {}
        for f in zpf.namelist():
            if f.split('.')[-1] in ['jpg', 'jpeg', 'png']:
                img_dir = str(os.path.join(settings.MEDIA_ROOT, 'img', str(id)))
                zpf.extract(f, img_dir)
                img_files.update({str(f.split('.')[0]): str(os.path.join(img_dir, f))})
        car_new.jdata_persons_photos = img_files
        car_new.save()

    return id
