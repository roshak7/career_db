import json
from datetime import datetime, date
import os
from django.conf import settings

from django.contrib.auth import logout
from django.contrib.auth import login
from django.http.response import JsonResponse, HttpResponse
from rest_framework import status, renderers
from rest_framework.decorators import api_view, renderer_classes, authentication_classes, permission_classes

from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.parsers import JSONParser
from rest_framework import permissions
from rest_framework import views
from rest_framework.response import Response
from career.add_to_node import line_add_to_position, line_add_to_successor
from career.edges.generator_edges import generate_edges
from career.map.map_zip_download import map_download_v2
from career.map.map_zip_upload import map_upload, map_upload_v2
from career.models import Career_data, Career_structure, Persons, Person_photo, Person_profile
from career.serializers import CareerSerializer, PersonSerializer, CardSerializer, LoginSerializer, UserLoginSerializer, \
    UserSerializer
from career.upload.parsing_ods import parsing_ods
from career.upload.parsing_xlsx import parsing_xlsx_file_2
from career.upload.upload import photo_load, photo_load_one, profile_load_one, delete_profile_file
from django.utils.encoding import escape_uri_path
from rest_framework.permissions import IsAuthenticated

from career.validations import validate_email, validate_password


class PNGRenderer(renderers.BaseRenderer):
    media_type = 'image/png'
    format = 'png'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


class JPGRenderer(renderers.BaseRenderer):
    media_type = 'image/jpg'
    format = 'jpg'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


def image_none():
    try:
        queryset = Person_photo.objects.get(idperson='none').img
        if not os.path.exists(queryset.path):
            queryset = open(os.path.join(settings.MEDIA_ROOT, 'img', 'none.jpg'), 'rb')
        data = queryset
    except:
        data = open(os.path.join(settings.MEDIA_ROOT, 'img', 'none.jpg'), 'rb')

    return data
@api_view(['GET'])
@renderer_classes([JPGRenderer])
def get_image(request, id):
    if request.method == 'GET':

        try:
            if "_" in id:
                id_map = id.split('_')[1]

                file_path = Career_structure.objects.get(id=int(id_map)).jdata_persons_photos[id.split('_')[0]]
                if not os.path.exists(file_path):
                    try:
                        f = Person_photo.objects.get(idperson='none').img
                        if not os.path.exists(f.path):
                            f = open(os.path.join(settings.MEDIA_ROOT, 'img', 'none.jpg'), 'rb')
                    except:
                        f = open(os.path.join(settings.MEDIA_ROOT, 'img', 'none.jpg'), 'rb')

                else:
                    f = open(file_path, 'rb')

                return Response(f, content_type='image/jpg')
        except:
            pass

        try:
            if "_" in id:
                id = id.split('_')[0]
            queryset = Person_photo.objects.get(idperson=id).img
            file_path = queryset.path
            if not os.path.exists(file_path):
                data = image_none()
            else:
                data = queryset


        except:
            data = image_none()



        return Response(data, content_type='image/jpg')


@api_view(['PUT'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def map_zip_upload(request):
    if request.method == 'PUT':
        file_list = request.FILES.getlist('file')
        res_list = []
        for file_obj in file_list:
            type_file = file_obj.name.split('.')[-1]

            if type_file in ['zip']:
                map_id = map_upload_v2(zip_file=file_obj)
            else:
                res_list.append({'file': file_obj.name, 'msg': 'Не поддерживаемый формат файла'})
                pass
        return JsonResponse({'report': 'Файлы загружены', 'result': res_list}, status=status.HTTP_200_OK)
    return JsonResponse({'errMsg': "Ошибка в загрузке файла"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def map_zip_download(request, id):
    if request.method == 'GET':
        return map_download_v2(id=id)


@api_view(['POST'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def career_create_new(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
        except:
            data = request.data
        id_person = data['id_person']
        name = data['name']
        id_career_card = int(data['id_career_card'])
        career_card = Career_structure.objects.get(pk=id_career_card)
        new_org_structure = []

        new_org_structure.append({'id': id_person, 'idParent': ''})
        new_scan_list = [id_person, ]
        org_structure = career_card.jdata_org_structure
        org_successor = career_card.jdata_org_successor
        new_org_successor = []
        for n in range(0, len(org_structure)):
            scan_list = new_scan_list
            new_scan_list = []
            for sl in scan_list:
                for org_suc in org_successor:
                    if org_suc['parentID'] == sl:
                        new_org_successor.append(org_suc)

                for n_o_s in org_structure:

                    if n_o_s['parentID'] == sl:
                        new_org_structure.append(n_o_s)
                        new_scan_list.append(n_o_s['id'])

        org_card = Career_structure.objects.create(jdata_org_structure=new_org_structure,
                                                   jdata_org_successor=new_org_successor, name=name)
        org_card.save()

        return JsonResponse({"id_card": org_card.id}, status=status.HTTP_201_CREATED)

    else:
        return JsonResponse({"msg": "Ошибка запроса"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def career_list(request):
    if request.method == 'GET':
        tutorials = Career_data.objects.all()

        title = request.query_params.get('title', None)
        if title is not None:
            tutorials = tutorials.filter(title__icontains=title)

        tutorials_serializer = CareerSerializer(tutorials, many=True)
        return JsonResponse(tutorials_serializer.data, safe=False)
        # 'safe=False' for objects serialization

    elif request.method == 'POST':

        try:
            data = JSONParser().parse(request)
        except:
            data = request.data

        return JsonResponse(data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def card_list(request):
    if request.method == 'GET':
        try:
            user = request.user
        except:
            user = None
        if user.is_anonymous or user.is_staff or user == None:
            card = Career_structure.objects.all()
        else:
            card = Career_structure.objects.filter(id_user=user)
        # title = request.query_params.get('title', None)
        # if title is not None:
        #     tutorials = tutorials.filter(title__icontains=title)

        card_serializer = CardSerializer(card, many=True)
        return JsonResponse(card_serializer.data, safe=False)
        # 'safe=False' for objects serialization

    elif request.method == 'POST':

        try:
            data = JSONParser().parse(request)
        except:
            data = request.data

        return JsonResponse(data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def card_list_auth(request):
    if request.method == 'GET':
        card = Career_structure.objects.all()

        # title = request.query_params.get('title', None)
        # if title is not None:
        #     tutorials = tutorials.filter(title__icontains=title)

        card_serializer = CardSerializer(card, many=True)
        return JsonResponse(card_serializer.data, safe=False, status=status.HTTP_200_OK)
        # 'safe=False' for objects serialization

    elif request.method == 'POST':

        # data = JSONParser().parse(request)
        # print(request.user)
        str = '{"username":"%s"}' % request.user
        data = json.loads(str)
        return JsonResponse(data, status=status.HTTP_200_OK)


@api_view(['GET'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def career_detail(request, pk):
    try:
        tutorial = Career_data.objects.get(pk=pk)
    except Career_data.DoesNotExist:
        return JsonResponse({'errMsg': 'Карта не найдена'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        tutorial_serializer = CareerSerializer(tutorial)
        return JsonResponse(tutorial_serializer.data)

    elif request.method == 'PUT':

        try:
            tutorial_data = JSONParser().parse(request)
        except:
            tutorial_data = request.data
        tutorial_serializer = CareerSerializer(tutorial, data=tutorial_data)
        if tutorial_serializer.is_valid():
            tutorial_serializer.save()
            return JsonResponse(tutorial_serializer.data)
        return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        tutorial.delete()
        return JsonResponse({'report': 'Карта удалена'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def career_detail_cards(request, pk):
    try:
        cards_successor = Career_structure.objects.get(pk=pk)
        # persons = Persons.objects.get(pk=pk)
        # persons_serializer = PersonSerializer(persons)
        p_list = []
        persons_list = []
        orgstr = cards_successor.jdata_org_structure
        orgsuc = cards_successor.jdata_org_successor
        for org_s in orgstr:
            # print(org_s)
            persons_list.append(org_s['id'])

        for org_suc in orgsuc:
            # print(org_suc)
            persons_list.append(org_suc['id'])

        for p in Persons.objects.filter(person_id__in=persons_list):
            data = PersonSerializer(p).data
            try:
                bday = data['birthday']
                bday_new = datetime.strptime(bday, '%Y-%m-%d').strftime('%d.%m.%Y')

                data.update({'birthday': bday_new})
            except:
                pass
            try:
                contract_end_date = data['contract_end_date']
                contract_end_date = datetime.strptime(contract_end_date, '%Y-%m-%d').strftime('%d.%m.%Y')
                data.update({'contract_end_date': contract_end_date})
            except:
                pass

            try:
                bday = data['birthday']
                bday_new = datetime.strptime(bday, '%Y-%m-%d')
                born = bday_new

            except:
                try:
                    born = datetime.strptime(data['birthday'], '%d.%m.%Y')
                except:
                    born = ''

            # born = datetime.strptime("1988-06-10", '%Y-%m-%d')
            today = date.today()
            if born != '':
                age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            else:
                age = ''
            data.update(({'age': age}))
            p_list.append(data)
        org_list = cards_successor.jdata_org_structure

        org_successor_list = cards_successor.jdata_org_successor
        for count, org2 in enumerate(org_successor_list):
            org_successor_list[count] = line_add_to_successor(org_successor_list[count])
        if cards_successor.jdata_card_changes != None:
            for count, org in enumerate(org_list):
                id_node = org['id']
                try:
                    person = Persons.objects.get(person_id=id_node)
                except:
                    continue
                for csl in cards_successor.jdata_card_changes:
                    try:
                        issuccessor = csl['data']['nodes'][0]['data']['isSuccessor']
                    except:
                        issuccessor = False

                    if csl['id'] == id_node and issuccessor == False:
                        # if csl['id'] == id_node and csl['data']['nodes'][0]['data']['isSuccessor'] == False:
                        try:
                            org_list[count] = {"h": 105, "w": 400, "x": csl['data']['nodes'][0]['position']['x'],
                                               "y": csl['data']['nodes'][0]['position']['y'], 'protect': org['protect'],
                                               "id": org['id'], 'img': '/api/v1/img/%s/' % person.person_id_photo,
                                               "parentID": org['parentID'], 'lr': org['lr'], 'ymax': org['ymax']}
                        except:
                            org_list[count] = {"h": 105, "w": 400, "x": csl['data']['nodes'][0]['position']['x'],
                                               "y": csl['data']['nodes'][0]['position']['y'], "id": org['id'],
                                               'img': '/api/v1/img/%s/' % person.person_id_photo,
                                               "parentID": org['parentID'],
                                               'lr': org['lr'], 'ymax': org['ymax']}

                    # Временная вставка координат
                    # org_list[count] = line_add_to_position(org_list[count], count)

                    # org_list[count].update({'circle_coordinate': [[100, 100], [200, 200], [100, 200]]})

            for count, org2 in enumerate(org_successor_list):
                id_node = org2['id']
                try:
                    person = Persons.objects.get(person_id=id_node)
                except:
                    continue
                for csl2 in cards_successor.jdata_card_changes:
                    try:
                        issuccessor = csl2['data']['nodes'][0]['data']['isSuccessor']
                    except:
                        issuccessor = False
                    # if csl2['id'] == id_node and csl2['data']['nodes'][0]['data']['isSuccessor'] == True:
                    if csl2['id'] == id_node and issuccessor == True:
                        org_successor_list[count] = {"h": 105, "w": 400, "x": csl2['data']['nodes'][0]['position']['x'],
                                                     "y": csl2['data']['nodes'][0]['position']['y'],
                                                     "id": org2['id'],
                                                     'img': '/api/v1/img/%s/' % person.person_id_photo,
                                                     "parentID": org2['parentID']}

                # Временная вставка координат
                org_successor_list[count] = line_add_to_successor(org_successor_list[count])
                # org_successor_list[count].update({'line_coordinate': [[100+500, 100+500], [200+500, 100+500], [200+500, 100+500], [200+500, 200+500], [200+500, 200+500], [100+500, 200+500]]})
                # org_successor_list[count].update({'circle_coordinate': [[100+500, 100+500], [200+500, 200+500], [100+500, 200+500]]})
                # print(org)
        # print(cards_successor.jdata_card_changes[0]['data']['nodes'][0]['position'])
        # y_max = org_list[0]['lr'][0]['h_sum'][-1]

        org_list = generate_edges(org_list)

        if len(org_list) < 12:
            org_list.append({"id": 'organization', 'name': cards_successor.company, 'x': -46, 'y': -260})
            org_list.append({"id": 'legend', 'name': 'Легенда', 'x': 2700, 'y': 990})
        elif len(org_list) >= 12:
            org_list.append({"id": 'organization', 'name': cards_successor.company, 'x': -46, 'y': -260})
            org_list.append({"id": 'legend', 'name': 'Легенда', 'x': 2700, 'y': -260})
        else:
            org_list.append({"id": 'organization', 'name': cards_successor.company, 'x': -46, 'y': -260})
            org_list.append({"id": 'legend', 'name': 'Легенда', 'x': 2700, 'y': 940})

        data = {"persons": p_list,
                "org_structure": org_list,
                "successor": cards_successor.jdata_org_successor,
                "changes": cards_successor.jdata_card_changes,
                "company": cards_successor.company,
                "card_name": cards_successor.name
                }

    except Career_data.DoesNotExist:
        return JsonResponse({'errMsg': 'Карта не найдена'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        cards_successor_serializer = CareerSerializer(cards_successor)
        return JsonResponse(data)  # , cards_successor_serializer.data

    elif request.method == 'PUT':
        try:
            tutorial_data = JSONParser().parse(request)
        except:
            tutorial_data = request.data
        tutorial_serializer = CareerSerializer(cards_successor, data=tutorial_data)
        if tutorial_serializer.is_valid():
            tutorial_serializer.save()
            return JsonResponse(tutorial_serializer.data)
        return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'GET', 'DELETE'])
def career_profile_file(request, personId=None):
    if request.method == 'PUT':
        # try:
        #     file = request.FILES.getlist('file')[0]
        #     peson_id = request.POST['personId']
        # except:
        data = request.data
        peson_id = data['personId']
        file = data['file']
        # data = json.loads(request.data['data'])
        type_file = file.name.split('.')[-1]
        res_list = []
        if type_file in ['jpg', 'png', 'jpeg', 'xlsx', 'ods', 'pdf', 'xls', 'doc', 'docx']:
            # вызываем загрузки фото
            try:
                profile_load_one(file, peson_id)
            except:
                return JsonResponse({'errMsg': "ID Сотрудника не найдено"}, status=status.HTTP_400_BAD_REQUEST)
            # photo = Person_photo.objects.get(idperson=peson_id)

            res_list.append({'file': file.name, 'msg': 'Загружен'})
            return JsonResponse({'report': 'Файлы загружены', 'result': res_list},
                                status=status.HTTP_200_OK)
        else:
            return JsonResponse({'errMsg': "Формат файла не поддерживается"}, status=status.HTTP_400_BAD_REQUEST)

        # return JsonResponse({'report': 'Профиль загружен', 'data': data}, status=status.HTTP_200_OK)
    if request.method == 'DELETE':
        try:
            data = JSONParser().parse(request)
        except:
            data = request.data
        try:
            id_person = data['personId']
            delete_profile_file(id_person)
            return JsonResponse({'report': 'Файл профиля удален'}, status=status.HTTP_200_OK)
        except:
            return JsonResponse({'errMsg': "Ошибка при удалении файла"}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        # data = JSONParser().parse(request)
        id_person = personId
        try:
            # id_person = data['personId']
            queryset = Person_profile.objects.get(idperson=id_person).profile_file
            file_path = queryset.path
            if not os.path.exists(file_path):
                return JsonResponse({'errMsg': "Файл не найден"}, status=status.HTTP_404_NOT_FOUND)

        except:
            return JsonResponse({'errMsg': "Файл не найден"}, status=status.HTTP_404_NOT_FOUND)

        file = str(queryset.name).split('/')[1]
        response = HttpResponse(queryset.file, content_type='application/force-download')
        response['Content-Disposition'] = f"attachment; filename*=utf-8''{escape_uri_path(file)}"

        return response

    return JsonResponse({'errMsg': "Ошибка в запросе"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'OPTIONS'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def career_profile(request):
    if request.method == 'POST':

        try:
            data = JSONParser().parse(request)
        except:
            data = request.data

        try:
            id_person = data['id_person']
            id_card = data['id_card']

            person = Persons.objects.get(person_id=id_person)

            data2 = PersonSerializer(person).data
            # data.update({'birthday': data['birthday']})
            try:
                bday = data2['birthday']
                bday_new = datetime.strptime(bday, '%Y-%m-%d').strftime('%d.%m.%Y')

                data2.update({'birthday': bday_new})

            except:
                pass

            try:
                bday = data2['birthday']
                bday_new = datetime.strptime(bday, '%Y-%m-%d')
                born = bday_new

            except:
                try:
                    born = datetime.strptime(data2['birthday'], '%d.%m.%Y')
                except:
                    born = ''

            try:
                contract_end_date = data2['contract_end_date']
                contract_end_date_new = datetime.strptime(contract_end_date, '%Y-%m-%d').strftime('%d.%m.%Y')

                data2.update({'contract_end_date': contract_end_date_new})

            except:
                pass

            # born = datetime.strptime("1988-06-10", '%Y-%m-%d')
            today = date.today()
            if born != '':
                age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            else:
                age = ''
            data2.update(({'age': str(age)}))

            card = Career_structure.objects.get(id=int(id_card))
            org_structure = card.jdata_org_structure
            org_successor = card.jdata_org_successor
            persons_list = []
            for org_s in org_structure:
                persons_list.append(org_s['id'])

            for org_suc in org_successor:
                # print(org_suc)
                persons_list.append(org_suc['id'])

            pers = Persons.objects.filter(person_id__in=persons_list)

            successors = []  # преемники
            is_successors = []  # у кого преемник

            for org_suc in org_successor:
                if org_suc['parentID'][0:20] == id_person[0:20]:
                    try:
                        per = pers.get(person_id=org_suc['id'])
                        successors.append({'name': per.person_name, 'readiness': per.readiness, 'id': per.person_id})
                    except:
                        pass
                if org_suc['id'][0:20] == id_person[0:20]:
                    try:
                        per = pers.get(person_id=org_suc['parentID'])
                        is_successors.append({'name': per.person_name, 'readiness': per.readiness, 'id': per.person_id})
                    except:
                        pass



        except:
            return JsonResponse({'errMsg': 'Не верный запрос'}, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({
            "person": data2,
            "successors": successors,
            "is_successor": is_successors,
            "img": "/api/v1/img/%s" % person.person_id_photo

        }, status=status.HTTP_200_OK)

    return JsonResponse({'errMsg': 'Не верный запрос'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def career_save(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
        except:
            data = request.data
        id_node = data['id']
        try:
            cs = Career_structure.objects.get(id=int(data['id_card']))
        except:
            return JsonResponse({'errMsg': 'Не верный запрос'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ch = -1
            chanhes = cs.jdata_card_changes
            for count, csl in enumerate(chanhes):
                if csl['id'] == id_node:
                    ch = count
                    break
            if ch > -1:
                chanhes[ch] = {"id": id_node, "data": data['data']}
            else:
                chanhes.append({"id": id_node, "data": data['data']})
            cs.jdata_card_changes = chanhes
            cs.save()
        except:
            cs.jdata_card_changes = [{"id": id_node, "data": data['data']}]
            cs.save()
        return JsonResponse({'report': 'Изменения внесены'})
    return JsonResponse({'errMsg': 'Не верный запрос'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'PUT'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def profile_photo_upload(request):
    if request.method == 'PUT':
        # file = request.FILES.getlist('file')[0]
        # peson_id = request.POST['personId'][0:20]
        # data = json.loads(request.data['data'])
        data = request.data
        peson_id = data['personId'][0:20]
        file = data['file']
        type_file = file.name.split('.')[-1]
        res_list = []
        if type_file in ['jpg', 'png', 'jpeg']:
            # вызываем загрузки фото
            photo_load_one(file, peson_id)
            # photo = Person_photo.objects.get(idperson=peson_id)

            res_list.append({'file': file.name, 'msg': 'Загружен'})
            return JsonResponse({'report': 'Файлы загружены', 'result': res_list},
                                status=status.HTTP_200_OK)

    return JsonResponse({'errMsg': "Ошибка в загрузке файла"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', 'PUT', 'OPTIONS'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def change_card(request):
    try:
        data = JSONParser().parse(request)
    except:
        data = request.data
    id_card = int(data['id_card'])
    if request.method == 'PUT':
        if data['name'] == None or data['name'] == '':
            return JsonResponse({"errMsg": "Наименование карты не может быть пустым"},
                                status=status.HTTP_400_BAD_REQUEST)
        try:
            cs = Career_structure.objects.get(id=id_card)
            cs.name = data['name']
            cs.save()
        except:
            return JsonResponse({'errMsg': "Не найдена карта с id=%s" % str(data['id_card'])},
                                status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse({'report': 'Изменения внесены', 'data': data}, status=status.HTTP_200_OK)
    if request.method == 'DELETE':
        try:
            cs = Career_structure.objects.get(id=id_card)
            cs.delete()
        except:
            return JsonResponse({'errMsg': "Не найдена карта с id=%s" % str(data['id_card'])},
                                status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse({'report': 'Карта с id=%s, удалена' % str(data['id_card']), 'data': data},
                            status=status.HTTP_200_OK)
    return JsonResponse({'errMsg': "Ошибка в запросе"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def file_upload(request):
    if request.method == 'PUT':
        # file_obj_1 = request.data
        data = request.data
        try:
            file_list = request.FILES.getlist('file')
            if len(file_list)>0:
                pass
            else:
                file_list = data['file']
        except:
            file_list = data['file']

        # data = request.data
        # file_list = data['file']
        res_list = []
        for file_obj in file_list:
            type_file = str(file_obj.name.split('.')[-1]).lower()

            if type_file in ['xlsx', 'jpg', 'png', 'jpeg', 'zip', 'ods']:
                if type_file == 'xlsx':
                    idcard = parsing_xlsx_file_2(file_obj, request)
                    if idcard[0] > 0:
                        res_list.append({'file': file_obj.name, 'report': idcard[1]['report']})
                    else:
                        res_list.append({'file': file_obj.name, 'errMsg': idcard[1]['errMsg']})
                elif type_file == 'ods':
                    idcard = parsing_ods(file_obj, request)
                    if idcard[0] > 0:
                        res_list.append({'file': file_obj.name, 'report': idcard[1]['report']})
                    else:
                        res_list.append({'file': file_obj.name, 'errMsg': idcard[1]['errMsg']})
                        # return JsonResponse({'id_card': idcard}, status=status.HTTP_201_CREATED)
                if type_file == 'zip':
                    map_upload(zip_file=file_obj)
                    # вызываем функцию распаковки пакета
                    return JsonResponse({'report': 'Пакетный файл загружен'}, status=status.HTTP_200_OK)
                if type_file in ['jpg', 'png', 'jpeg']:
                    # вызываем загрузки фото
                    photo_load(file_obj)
                    res_list.append({'file': file_obj.name, 'report': 'Загружен'})
                    # return JsonResponse({'report': 'Фотография загружена'}, status=status.HTTP_200_OK)
            else:
                res_list.append({'file': file_obj.name, 'report': 'Не поддерживаемый формат файла'})
                # return JsonResponse({'error': 'Не поддерживаемый формат файла'},
                #                     status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
                pass
        return JsonResponse({'result': res_list}, status=status.HTTP_200_OK)
    return JsonResponse({'errMsg': "Ошибка в загрузке файла"}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(views.APIView):
    # This view should be accessible also for unauthenticated users.
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = LoginSerializer(data=self.request.data,
                                     context={'request': self.request})

        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            role = "admin" if user.is_staff else "user"
            context = {"name": user.username, "role": role, "email": user.email, "fio": user.first_name, "id": user.id}

            return Response(context, status=status.HTTP_202_ACCEPTED)
        else:
            context = {"errMsg": "Неправильное имя пользователя или пароль"}
            return Response(context, status=status.HTTP_401_UNAUTHORIZED)


class UserView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    ##
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)


class Logout(views.APIView):
    def get(self, request, format=None):
        # simply delete the token to force a login
        logout(request)
        return Response(status=status.HTTP_200_OK)
