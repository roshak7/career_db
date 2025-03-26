import mimetypes
import os
from datetime import date, datetime

from django.db.models import Q
from django.http.response import JsonResponse, HttpResponse
from rest_framework import status, renderers
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.parsers import JSONParser, FileUploadParser, FormParser, MultiPartParser
from rest_framework.response import Response

from api.views import person_l, person_data
from career.map.map_zip_upload import map_upload, map_upload_v2
from career.math.alg1_2 import *
from career.models import *
from career.serializers import CardSerializer, PersonSerializer
from career.upload.nsi import update_si_organization, update_si_organization_1
from career.upload.parsing_ods import parsing_ods
from career.upload.parsing_xlsx import parsing_xlsx_file_2
from career.upload.upload import photo_load
from career.upload.utils import ready


def get_profile_jf(uid=None):
    jprofile = False
    profile = False
    try:
        pf = Person_profile.objects.get(idperson__istartswith=uid[0:20])
        if pf.jdata != None:
            jprofile = True
        if len(pf.profile_file.name) > 1:
            profile = True
    except Exception as e:
        pass

    return {'profile': profile, 'jprofile': jprofile}


def data_get(idorg=None, iddep=None, idpos=None, idpers=None):

    data={}
    if idpers != None:
        idpers=int(idpers)
        pers = SPerson.objects.get(id=idpers)
        data.update(pers.jdata)
        data.update({'idpers': idpers})
        # data.update(get_profile_jf(pers.uid))
        data.update({"img": f"/api/v1/img/{pers.uid}"})
        try:
            today = date.today()

            birthday = pers.jdata['birthday']
            born = datetime.strptime(birthday, '%d.%m.%Y')
            # born = bday_new
            if born != '':
                age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            else:
                age = ''
            data.update({"age": age})
        except:
            pass

    if idorg != None:
        idorg=int(idorg)
        org = SOrganization.objects.get(id=idorg)
        organization_name = org.name
        data.update({"organization_name": organization_name})

    if iddep != None:
        iddep=int(iddep)
        dep = SDepartment.objects.get(id=iddep)
        department_full_name = dep.jdata['value']
        department_short_name = dep.jdata['shortValue']
        data.update({"department_short_name": department_short_name, "department_full_name": department_full_name})

    if idpos != None:
        idpos = int(idpos)
        pos = SPosition.objects.get(id=int(idpos))
        position_full_name = pos.jdata['value']
        position_short_name = pos.jdata['shortValue']
        try:
            position_critical = pos.jdata['position_critical']
        except:
            position_critical = 'Нет'

        data.update({"position_full_name": position_full_name, "position_short_name": position_short_name,
                     "position_critical": position_critical})



    if idpers == None:
        name = "Вакансия"
        m = hashlib.md5()
        m.update(name.lower().encode("utf8"))
        uidvac = m.hexdigest()[0:20]
        data_vac = {"uid": uidvac, "person_fio": name, "person_name": name}

        obj, created = SPerson.objects.update_or_create(
            uid=uidvac,
            defaults={'jdata': data_vac, 'name': name},
        )
        data.update(data_vac)
        data.update({"img": f"/api/v1/img/{uidvac}"})
        # data.update({"iddep": iddep, "idorg": idorg, "idpos": idpos})

    data.update({"iddep": iddep, "idorg": idorg, "idpos": idpos, "idpers":idpers})
    return data


def protect_d(suc_count, ready_list):
    ########################################
    #  Определяем степень защиты должности #
    ########################################
    '''
    Для 3-видов защищенностей:
        (зел) Должность защищена: утвержден один преемник (готовность не более 1 года)
        (жел) Должность частично защищена: утвержден один преемник (готовность более 1 года)
        (красн) Должность не защищена: преемники не утверждены

    Для 4-видов защищенностей:
        (1. синий) Должность полностью защищена: утверждены два преемника один из них почти готов (готовность не более 1 года)
        (2. зел) Должность защищена: утвержден один преемник (готовность не более 1 года)
        (жел) Должность частично защищена: утвержден один преемник (готовность более 1 года)
        (4. красн) Должность не защищена: преемники не утверждены

    Для 4-х видов добавится protect = 0 - это должен быть синий
    Для этого необходимо поставить условие suc_count > 1 и min(ready_list)==0
    '''
    if len(ready_list) == 0:
        m = 0
    else:
        m = min(ready_list)

    if suc_count < 1:
        protect = 4
    else:

        if m <= 1 and suc_count >= 1:
            protect = 2
        else:
            protect = 3
    if suc_count > 1 and m == 0:
        protect = 1

    return protect

def test1(request):
    update_si_organization()
    return JsonResponse({'name': 'ok'}, status=status.HTTP_200_OK)


def tes_succ():
    cards_successor = Career_structure.objects.get(pk=744)
    org_list = cards_successor.jdata_org_structure
    org_successor_list = cards_successor.jdata_org_successor
    jdata = []
    for dorg in org_list:
        succ = 0
        for dsuc in org_successor_list:
            if dsuc['parentID'] == dorg['id']:
                succ += 1
        jdata.append({'id': dorg['id'], 'parentID': dorg['parentID'], 'succ': succ})

    jdata = placement_coordinate(jdata)


@api_view(['GET'])
def information(request):
    try:
        username = str(request.user)
        from .version import __version__
        version = __version__
        return JsonResponse({'name': username, 'fio': 'ФИО', 'role': 'user', 'version': version},
                            status=status.HTTP_200_OK)
    except Career_structure.DoesNotExist:
        return JsonResponse({'errMsg': 'Карта не найдена'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def career_map_save(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
        except:
            data = request.data
        id = data['id']
        try:
            cs = Career_structure.objects.get(id=int(id))
        except:
            return JsonResponse({'errMsg': 'Карта не найдена'}, status=status.HTTP_404_NOT_FOUND)

        try:
            new_md = []
            try:
                for d in data['cellsMetadata']['nodesMetadata']:
                    d['data'].update(get_profile_jf(d['data']['person_id']))
                    d['data'].update({'uid': d['data']['person_id']})
                    new_md.append(d)
                data['cellsMetadata']['nodesMetadata'] = new_md
            except:
                pass

            cs.jdata_card_changes = data
            if cs.draft == True and cs.jdata_card_default == None:
                cs.jdata_card_default = data
                cs.draft = False
            cs.save()
        except:
            JsonResponse({'errMsg': 'Не верный запрос'}, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse({'report': 'Изменения внесены'})
    return JsonResponse({'errMsg': 'Не верный запрос'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def career_map_check(request, pk):
    try:
        cards_successor = Career_structure.objects.get(pk=pk)
        return JsonResponse({'report': 'Карта существует'}, status=status.HTTP_200_OK)
    except Career_structure.DoesNotExist:
        return JsonResponse({'errMsg': 'Карта не найдена'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def career_map(request, pk):
    shapes = ['node_top', 'node_position', 'node_successor', 'node_title', 'node_legend']
    id_map = ''

    try:
        # Получаем объект с данными по карте id=pk
        cards_successor = Career_structure.objects.get(pk=pk)
    except Career_structure.DoesNotExist:
        return JsonResponse({'errMsg': 'Карта не найдена'}, status=status.HTTP_404_NOT_FOUND)

    data = {}
    if request.method == 'GET':
        if cards_successor.draft == True:
            data = {}
            data.update({
                "draft": cards_successor.draft,
                # "parent": str(cards_successor.id_folder) + '_f',
                "type_map": cards_successor.type_map,
                "card_name": cards_successor.name,
                "company": cards_successor.company,
                "data": cards_successor.jdata_card_draft
            })
            return JsonResponse(data, status=status.HTTP_200_OK)
        if cards_successor.jdata_org_structure == None:
            data = {}
            default_stat = cards_successor.jdata_card_default['statistics']
            stat_save = cards_successor.jdata_card_changes['statistics']
            cellsmetadata_default = None
            cellsmetadata_save = None
            if cards_successor.jdata_card_changes != None:
                cellsmetadata_default = cards_successor.jdata_card_default['cellsMetadata']
                cellsmetadata_save = cards_successor.jdata_card_changes['cellsMetadata']
                try:
                    if str(cards_successor.jdata_card_changes['id']) == str(pk):
                        cellsmetadata_save = {
                            'nodesMetadata': cards_successor.jdata_card_changes['cellsMetadata']['nodesMetadata'],
                            'edgesMetadata': cards_successor.jdata_card_changes['cellsMetadata']['edgesMetadata']}
                    stat_save = cards_successor.jdata_card_changes["statistics"]
                except:
                    cellsmetadata_save = cellsmetadata_default

            if cellsmetadata_save == None:
                cellsmetadata_save = cellsmetadata_default
            # new_md=[]
            # for d in cellsmetadata_save['nodesMetadata']:
            #     try:
            #         d['data'].update(get_profile_jf(d['data']['person_id']))
            #         new_md.append(d)
            #     except:
            #         new_md.append(d)
            #
            # cellsmetadata_save['nodesMetadata'] = new_md
            data.update({
                "parent": str(cards_successor.id_folder) + '_f',
                "cellsMetadata": cellsmetadata_save,
                "cellsMetadataDefault": cellsmetadata_default,
                "company": cards_successor.company,
                "card_name": cards_successor.name,
                "type_map": cards_successor.type_map,
                "stat": {"default": default_stat, "current": stat_save}
            })
            return JsonResponse(data, status=status.HTTP_200_OK)
    try:
        type_map = cards_successor.type_map
        if type_map == None:
            type_map = 'singlelevel'
        org_name = cards_successor.company
        # Получаем данными по должностям
        org_list = cards_successor.jdata_org_structure
        if org_list == None:
            org_list = []
        # Получаем данными по преемникам
        org_successor_list = cards_successor.jdata_org_successor
        if org_successor_list == None:
            org_successor_list = []
        jdata = []
        # создаем модель данных по должностям
        for dorg in org_list:
            succ = 0
            for dsuc in org_successor_list:
                if dsuc['parentID'] == dorg['id']:
                    succ += 1
            jdata.append({'id': dorg['id'], 'parentID': dorg['parentID'], 'succ': succ})

        persons_list, p_list, p_list_kvd = person_l(org_list, org_successor_list, org_name)

        if cards_successor.jdata_persons is not None:
            p_list = cards_successor.jdata_persons
            id_map = '_' + str(pk)
        # расставляем координаты для созданной модели данных
        try:
            jdata = placement_coordinate(jdata)
        except:
            jdata = []

        org_list = []
        org_succ = []
        x_max = 0
        boss_xmax = 0
        pr = [0, 0, 0, 0]
        readiness_l = [0, 0, 0, 0, 0, 0]
        x_boss = jdata[0]['boss'][0][0]
        edges = []
        for cn, j in enumerate(jdata):
            boss_xmax = max(boss_xmax, j['boss'][0][0])
            id_node = j['id']
            p_photo = 'none'
            p_d = {}
            port = {}

            try:
                p_d = person_data(p_list, id_node)
                uid_d = p_d['person_id']
                p_d.update({'uid': p_d['person_id']})
                p_d.update(get_profile_jf(uid_d))

                p_photo = p_d['person_id_photo'] + id_map
            except:
                pass

            ready_list = []
            if cn > 0:
                shape = shapes[1]

                port = {
                    'items': [

                        {
                            'id': id_node,
                            'group': 'top',
                        }]}
                edges.append({'shape': 'edge_position', 'source': {'cell': id_node, 'port': id_node},
                              # 'target': {'cell': jdata[0]['id'], 'port': jdata[0]['id']},
                              'target': {'cell': j['parentID'], 'port': j['parentID']},
                              'vertices': [], 'id': str(id_node) + '_@4#@_' + str(j['parentID'])})

            else:
                shape = shapes[0]
                port = {
                    'items': [
                        {
                            'id': jdata[0]['id'],
                            'group': 'bottom',
                        }
                    ]}
            if len(j['r_size']) > 0:
                port['items'].append({
                    'id': id_node + '_r',
                    'group': 'right',
                })
            if len(j['l_size']) > 0:
                port['items'].append({
                    'id': id_node + '_l',
                    'group': 'left',
                })

            dir_photo = "/api/v1/img/" + p_photo + '/'
            p_d.update({"img": dir_photo})
            # print(p_d)
            json_new = {"h": 105, "w": 400, "x": j['boss'][0][0],
                        "y": j['boss'][0][1], "id": id_node, 'shape': shape,
                        "parentID": j['parentID'],
                        'data': p_d, 'ports': port}
            # try:
            # json_new.update({'edges2': [[x_boss / 10 + 24.85, j['y1'] / 10 + 4.5],
            #                             [j['boss'][0][0] / 10 + 24.85, j['y1'] / 10 + 4.5]]})

            # except:
            #     pass

            if j['succ'] > 0:
                count_s = 0
                c_pos = 0
                for osl in org_successor_list:
                    p_dict = {}

                    s_photo = 'none'

                    if j['id'] == osl['parentID']:
                        c_pos += 1
                        if c_pos > 4:
                            pos = 'l'
                            group = 'right'
                        else:
                            pos = 'r'
                            group = 'left'
                        try:
                            p_dict = person_data(p_list, osl['id'])
                            readiness = p_dict['readiness']
                            uid_p = p_dict['person_id']
                            p_dict.update({'uid': uid_p})
                            p_dict.update(get_profile_jf(uid_p))
                            ready_list.append(ready(readiness))
                            s_photo = p_dict['person_id_photo'] + id_map
                        except:
                            pass
                        x, y = j['suxy'][count_s]
                        x_max = max(x_max, x)
                        dir_photo = "/api/v1/img/" + s_photo + '/'
                        p_dict.update({"img": dir_photo})
                        # print(p_dict)
                        if pos == 'r':
                            port_pos = '_l'
                        else:
                            port_pos = '_r'
                        port_edge = {
                            'items': [
                                {
                                    'id': osl['id'] + port_pos,
                                    'group': group,
                                }
                            ]}

                        org_succ.append({"w": 400, "x": x, "y": y, 'shape': shapes[2],
                                         "id": osl['id'], "parentID": osl['parentID'],
                                         "order_number": 1, 'pos': pos,
                                         'data': p_dict, 'ports': port_edge})

                        edges.append(
                            {'shape': 'edge_successor', 'source': {'cell': osl['id'], 'port': osl['id'] + port_pos},
                             'target': {'cell': osl['parentID'], 'port': osl['parentID'] + '_' + pos},
                             'vertices': [], 'id': str(osl['id']) + '_@3#@_' + str(osl['parentID'])})
                        count_s += 1
            protect = protect_d(j['succ'], ready_list)
            json_new['data'].update({"protect": protect})
            pr[protect - 1] += 1
            for n1 in ready_list:
                readiness_l[n1] += 1
            json_new.update({'protect': protect})
            json_new['data'].update({'uid': json_new['data']['person_id']})
            json_new['data'].update(get_profile_jf(json_new['data']['person_id'][0:20]))

            org_list.append(json_new)
        total_positions = len(org_list)
        pr_dict = {}
        read_dict = {}
        for ip in range(0, len(pr)):
            pr_dict.update({"p%d" % ip: pr[ip]})
        for lp in range(0, len(readiness_l)):
            read_dict.update({"p%d" % lp: readiness_l[lp]})
        org_list.append(
            {"id": 'organization', 'data': {'name': cards_successor.company}, 'x': 0, 'y': 0, 'shape': shapes[3]})
        if x_max < boss_xmax:
            x_max = boss_xmax
        if len(jdata) > 1:
            org_list.append({"id": 'legend', 'data': {'name': 'Легенда'}, 'x': x_max - 200, 'y': 0, 'shape': shapes[4]})
        else:
            org_list.append({"id": 'legend', 'data': {'name': 'Легенда'}, 'x': x_max + 200, 'y': 0, 'shape': shapes[4]})
        # org_list = edges_correct(jdata, org_list)
        cellsmetadata_save = None

        try:
            org_list += org_succ
        except:
            pass

        total_successors = len(org_succ)
        cellsmetadata_default = {'nodesMetadata': org_list, 'edgesMetadata': edges}
        data = {}

        if cards_successor.type_map == 'multilevel':
            if cards_successor.jdata_card_changes == None:
                data.update({'shouldPreprocess': True})
            else:
                data.update({'shouldPreprocess': False})
        default_stat = {"total_positions": total_positions, "total_successors": total_successors, "protect": pr_dict,
                        "ready": read_dict, "total_critical": len(p_list_kvd)}
        stat_save = default_stat
        if cards_successor.jdata_card_changes != None:
            try:
                if str(cards_successor.jdata_card_changes['id']) == str(pk):
                    cellsmetadata_save = {
                        'nodesMetadata': cards_successor.jdata_card_changes['cellsMetadata']['nodesMetadata'],
                        'edgesMetadata': cards_successor.jdata_card_changes['cellsMetadata']['edgesMetadata']}
                stat_save = cards_successor.jdata_card_changes["statistics"]
            except:
                cellsmetadata_save = cellsmetadata_default

        if cellsmetadata_save == None:
            cellsmetadata_save = cellsmetadata_default

        data.update({
            "parent": str(cards_successor.id_folder) + '_f',
            "cellsMetadata": cellsmetadata_save,
            "cellsMetadataDefault": cellsmetadata_default,
            "company": cards_successor.company,
            "card_name": cards_successor.name,
            "type_map": type_map,
            "stat": {"default": default_stat, "current": stat_save}
        })



    except Exception as e:
        # print(e)
        return JsonResponse({'errMsg': 'Ошибка запроса'}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        # cards_successor_serializer = CareerSerializer(cards_successor)
        return JsonResponse(data)  # , cards_successor_serializer.data


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


@api_view(['POST'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def card_list_tree_new_map(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
        except:
            data = request.data
        # person_id = data.get('person_id', None)
        # position_id = data.get('position_id', None)
        idorg = data.get('organization', None)
        iddep = data.get('department', None)
        idpos = data.get('position', None)
        idpers = data.get('person', None)
        jdata = data_get(idorg, iddep, idpos, idpers)
        company = jdata['organization_name']

        if data['parent'] == '0' or data['parent'] == '' or data['parent'] == None:
            idparent = None
            # idp = idparent
        else:
            idparent = int(data['parent'][0:-2])

        cs = Career_structure(type_map=data['type_map'], id_folder=idparent, jdata_card_draft=jdata,
                              company=company, name=data['card_name'], draft=True)
        cs.save()

        return JsonResponse({'id': str(cs.id)}, status=status.HTTP_200_OK)


from rest_framework.views import APIView


class FileUploadView(APIView):
    parser_classes = [FormParser, MultiPartParser]

    def post(self, request):
        return JsonResponse({'result': "res_list"}, status=status.HTTP_200_OK)


@api_view(['PUT', 'GET'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def card_list_tree_add_maps(request):
    data = request.data

    if request.method == 'PUT':
        action = data.get('action', 'addmap')
        idparent = data.get('idparent', None)
        try:
            file_list = request.FILES.getlist('file')
            if len(file_list) > 0:
                pass
            else:
                file_list = data['file']
        except:
            file_list = data['file']
        if action == 'addmap':
            res_list = []
            if idparent == '0' or idparent == '' or idparent == None or idparent == 'none':
                idparent = None
            else:
                idparent = int(idparent[0:-2])

            for file_obj in file_list:
                type_file = str(file_obj.name.split('.')[-1]).lower()

                if type_file in ['xlsx', 'zip', 'ods', 'jpg', 'jpeg', 'png']:
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
                    elif type_file in ['jpg', 'png', 'jpeg']:
                        # вызываем загрузки фото
                        photo_load(file_obj)
                        res_list.append({'file': file_obj.name, 'report': 'Загружен'})
                    elif type_file == 'zip':
                        idcard = map_upload_v2(zip_file=file_obj)
                        if idcard[0] > 0:
                            res_list.append({'file': file_obj.name, 'report': idcard[1]['report']})
                        else:
                            res_list.append({'file': file_obj.name, 'report': 'Ошибка загрузки пакетного файла ZIP'})
                    try:
                        if idcard[0] > 0:
                            id = int(idcard[0])
                            bob = Career_structure.objects.get(id=id)
                            bob.id_folder = idparent
                            bob.save(update_fields=["id_folder"])
                    except:
                        pass


                else:
                    res_list.append({'file': file_obj.name, 'report': 'Не поддерживаемый формат файла'})
                    # return JsonResponse({'error': 'Не поддерживаемый формат файла'},
                    #                     status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

            return JsonResponse({'result': res_list}, status=status.HTTP_200_OK)

        else:
            return JsonResponse({'errMsg': 'Не корректно указан Action'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def card_list_tree(request):
    if request.method == 'GET':
        card = Career_structure.objects.all()
        card = card.order_by('name')

        folders = []
        cards = []
        folder = TreeFolders.objects.all()
        folder = folder.order_by('name')
        for ff in folder:
            if ff.parent_id == None or ff.parent_id == 0:
                parent = "0"
            else:
                parent = str(ff.parent_id) + "_f"
            folders.append({"text": ff.name, "id": str(ff.id) + "_f", "parent": parent, "droppable": True})

        for c in card:
            id_folder = c.id_folder
            if id_folder == None or id_folder == 0:
                idf = "0"
            else:
                idf = str(id_folder) + "_f"

            cards.append({"id": str(c.id) + "_m", "text": c.name, "parent": idf})

        folders = folders + cards
        return JsonResponse(folders, safe=False)

    elif request.method == 'POST':

        try:
            data = JSONParser().parse(request)
        except:
            data = request.data

        action = data['action']
        if action == 'changename':

            if data['name'] == '' or data['name'] == None:
                return JsonResponse({'errMsg': 'Не корректно поле Name'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                if data['id'][-1] == 'm':
                    # если это id карты
                    id = int(data['id'][0:-2])
                    bob = Career_structure.objects.get(id=id)
                    bob.name = data['name']
                    bob.save(update_fields=["name"])
                    return JsonResponse({'report': 'Имя карты изменено'}, status=status.HTTP_200_OK)
                elif data['id'][-1] == 'f':
                    # если это id папки
                    id = int(data['id'][0:-2])
                    bob = TreeFolders.objects.get(id=id)
                    bob.name = data['name']
                    bob.save(update_fields=["name"])
                    return JsonResponse({'report': 'Имя папки изменено'}, status=status.HTTP_200_OK)
                else:
                    return JsonResponse({'errMsg': 'Не корректный ID'}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return JsonResponse({'errMsg': 'Не корректный ID'}, status=status.HTTP_400_BAD_REQUEST)

        elif action == 'move':

            # if data['idparent'] == '' or data['idparent'] == None:
            #     return JsonResponse({'errMsg': 'Не корректное поле idparent'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                if data['idparent'] == '0' or data['idparent'] == '' or data['idparent'] == None:
                    idparent = None
                    idp = idparent
                else:
                    idparent = int(data['idparent'][0:-2])
                    idp = TreeFolders.objects.get(id=idparent)

                if data['id'][-1] == 'm':
                    # если это id карты
                    id = int(data['id'][0:-2])
                    bob = Career_structure.objects.get(id=id)
                    bob.id_folder = idparent
                    bob.save(update_fields=["id_folder"])
                    return JsonResponse({'report': 'idparent у карты изменен'}, status=status.HTTP_200_OK)
                elif data['id'][-1] == 'f':
                    # если это id папки
                    id = int(data['id'][0:-2])
                    bob = TreeFolders.objects.get(id=id)
                    bob.parent = idp
                    bob.save(update_fields=["parent"])
                    return JsonResponse({'report': 'idparent у папки изменен'}, status=status.HTTP_200_OK)
                else:
                    return JsonResponse({'errMsg': 'Не корректный ID'}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return JsonResponse({'errMsg': 'Не корректный ID'}, status=status.HTTP_400_BAD_REQUEST)

        elif action == 'delete':
            try:
                list_obj = data['data']
                for obj in list_obj:
                    try:
                        if obj['id'][-1] == 'm':
                            # если это id карты
                            id = int(obj['id'][0:-2])
                            Career_structure.objects.filter(id=id).delete()

                        elif obj['id'][-1] == 'f':
                            # если это id папки
                            id = int(obj['id'][0:-2])
                            TreeFolders.objects.filter(id=id).delete()

                        else:
                            return JsonResponse({'errMsg': 'Не корректный ID'}, status=status.HTTP_400_BAD_REQUEST)
                    except Exception as e:
                        return JsonResponse({'errMsg': e}, status=status.HTTP_400_BAD_REQUEST)

                return JsonResponse({'report': 'Удаление всех объектов прошло успешно'}, status=status.HTTP_200_OK)
            except:
                return JsonResponse({'errMsg': 'Не корректный запрос'}, status=status.HTTP_400_BAD_REQUEST)
        elif action == 'addfolder':
            if data['idparent'] == '' or data['idparent'] == None:
                return JsonResponse({'errMsg': 'Не корректное поле idparent'}, status=status.HTTP_400_BAD_REQUEST)
            if data['name'] == '' or data['name'] == None:
                return JsonResponse({'errMsg': 'Не корректно поле Name'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                if data['idparent'] == '0':
                    bob = TreeFolders(name=data['name'])
                    bob.save()
                else:
                    idparent = int(data['idparent'][0:-2])
                    idp = TreeFolders.objects.get(id=idparent)
                    bob = TreeFolders(name=data['name'], parent=idp)
                    bob.save()

            except:
                return JsonResponse({'errMsg': 'Ошибка запроса'}, status=status.HTTP_400_BAD_REQUEST)
            return JsonResponse({'report': 'Папка добавлена'}, status=status.HTTP_200_OK)

            # return JsonResponse({'report': 'Карта добавлена'}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'errMsg': 'Не корректно указан Action'}, status=status.HTTP_400_BAD_REQUEST)

        # return JsonResponse({'errMsg': 'Ошибка запроса'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def position_search(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
        except:
            data = request.data
        company_id = data['company_id']
        search_str = data['search_str']
        result = []
        pos = SPosition.objects.all()
        for p in pos:
            if str(search_str).lower() in str(p.name).lower():
                result.append({'id': p.uid, 'position_full_name': p.name})

        return JsonResponse(result, safe=False)


@api_view(['POST'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def person_search(request):
    if request.method == 'POST':

        try:
            data = JSONParser().parse(request)
        except:
            data = request.data
        company_id = data['company_id']
        search_str = data['search_str']
        person = Persons.objects.filter(person_fio__icontains=search_str.lower())
        result = []
        for p in person:
            result.append({'id': p.person_id, 'person_fio': p.person_fio})

        return JsonResponse(result, safe=False)


@api_view(['POST'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def get_person_data(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
        except:
            data = request.data
        person_id = data['person_id']
        person = Persons.objects.get(person_id=person_id)

        data2 = PersonSerializer(person).data
        return JsonResponse(data2, safe=False)


@api_view(['POST'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def get_position_data(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
        except:
            data = request.data
        position_id = data['position_id']
        position = {}
        pos = SPosition.objects.all()
        for p in pos:
            if position_id == p.uid:
                position = {'position_full_name': p.name}
        return JsonResponse(position, safe=False)


@api_view(['PUT', 'GET', 'DELETE', 'POST'])
def s_organization(request):
    try:
        if request.method == 'GET':
            sorg = SOrganization.objects.all()
            jlist = []
            for s in sorg:
                j = {}
                jdata = s.jdata
                j.update({'id': s.id, 'uid': s.uid})
                j.update(jdata)
                jlist.append(j)

            return JsonResponse(jlist, safe=False, status=status.HTTP_200_OK)

        if request.method == 'POST':
            try:
                data = JSONParser().parse(request)
            except:
                data = request.data
            sorg = SOrganization(jdata=data)
            sorg.save()
            j = {}
            jdata = sorg.jdata
            j.update({'id': sorg.id, 'uid': sorg.uid})
            j.update(jdata)
            return JsonResponse(j, status=status.HTTP_201_CREATED)

        if request.method == 'PUT':
            try:
                data = JSONParser().parse(request)
            except:
                data = request.data
            sorg = SOrganization.objects.get(id=int(data['id']))
            del data['id']
            sorg.jdata = data
            sorg.save()
            return JsonResponse({'report': 'Запись изменена'}, status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            try:
                data = JSONParser().parse(request)
            except:
                data = request.data
            sorg = SOrganization.objects.get(id=int(data['id']))
            sorg.delete()

            return JsonResponse({'report': 'Запись удалена'}, status=status.HTTP_200_OK)
        return JsonResponse({'errMsg': 'Ошибка в запросе'}, status=status.HTTP_400_BAD_REQUEST)
    except:

        return JsonResponse({'errMsg': 'Ошибка в запросе'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'GET', 'DELETE', 'POST'])
def s_position(request):
    try:
        if request.method == 'GET':
            idorg = request.GET.get('idorg', None)
            iddep = request.GET.get('iddep', None)
            search = request.GET['query']
            if iddep == None:
                spos = SPosition.objects.filter(id_sorganization_id=int(idorg), name__icontains=search)
            else:
                spos = SPosition.objects.filter(id_sorganization_id=int(idorg), id_sdepartment_id=int(iddep),
                                            name__icontains=search)
            jlist = []
            for s in spos:
                j = {}
                jdata = s.jdata
                j.update({'id': s.id, 'uid': s.uid})
                j.update(jdata)
                jlist.append(j)

            return JsonResponse(jlist, safe=False, status=status.HTTP_200_OK)

        if request.method == 'POST':
            try:
                data = JSONParser().parse(request)
            except:
                data = request.data

            sp = SPosition.objects.filter(jdata=data)
            if len(sp) > 0:
                spos = sp.first()
            else:
                spos = SPosition(jdata=data)
                spos.save()
            j = {}
            jdata = spos.jdata
            j.update({'id': spos.id, 'uid': spos.uid})
            j.update(jdata)

            return JsonResponse(j, status=status.HTTP_201_CREATED)

        if request.method == 'PUT':
            try:
                data = JSONParser().parse(request)
            except:
                data = request.data
            spos = SPosition.objects.get(id=int(data['id']))
            del data['id']
            spos.jdata = data
            spos.save()
            return JsonResponse({'report': 'Запись изменена'}, status=status.HTTP_204_NO_CONTENT)

        if request.method == 'DELETE':
            try:
                data = JSONParser().parse(request)
            except:
                data = request.data
            spos = SPosition.objects.get(id=int(data['id']))
            spos.delete()

            return JsonResponse({'report': 'Запись удалена'}, status=status.HTTP_200_OK)
        return JsonResponse({'errMsg': 'Ошибка в запросе'}, status=status.HTTP_400_BAD_REQUEST)
    except:

        return JsonResponse({'errMsg': 'Ошибка в запросе'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'GET', 'DELETE', 'POST'])
def s_department(request):
    # try:
    if request.method == 'GET':
        # try:
        id = request.GET.get('id', None)
        jdata = {}
        uidorg = request.GET.get('uidOrg', None)
        uidperson = request.GET.get('uidPerson', None)
        idorg = request.GET.get('idorg', None)
        search = request.GET.get('query', None)
        if id != None:
            sdep = SDepartment.objects.get(id=int(id))
            jdata.update({'id': id})
            jdata.update(sdep.jdata)
            return JsonResponse(jdata, safe=False, status=status.HTTP_200_OK)
        if uidorg != None:
            sdep = SDepartment.objects.filter(id_sorganization__uid=uidorg, name__icontains=search)
        elif idorg != None:
            sdep = SDepartment.objects.filter(id_sorganization_id=int(idorg), name__icontains=search)
        elif uidperson != None:
            uid_org = update_si_organization_1(uidperson)[0]
            sdep = SDepartment.objects.filter(id_sorganization__uid=uid_org, name__icontains=search)



        else:
            return JsonResponse({'errMsg': 'Ошибка в запросе'}, status=status.HTTP_400_BAD_REQUEST)

        # except:
        #     sdep = SDepartment.objects.all()[0:10]
        jlist = []
        for s in sdep:
            j = {}
            jdata = s.jdata
            j.update({'id': s.id, 'uid': s.uid})
            j.update(jdata)
            jlist.append(j)

        return JsonResponse(jlist, safe=False, status=status.HTTP_200_OK)

    if request.method == 'POST':

        try:
            data = JSONParser().parse(request)
        except:
            data = request.data
        idperson = data.get('uidPerson', None)
        if idperson != None:
            id_org = update_si_organization_1(data['uidPerson'])[11]
            data.update({'idorg': id_org})

        sdep = SDepartment(jdata=data)
        sdep.save()
        j = {}
        jdata = sdep.jdata
        j.update({'id': sdep.id, 'uid': sdep.uid})
        j.update(jdata)
        return JsonResponse(j, status=status.HTTP_201_CREATED)

    if request.method == 'PUT':
        try:
            data = JSONParser().parse(request)
        except:
            data = request.data
        iddep = data.get('id', None)
        uiddep = data.get('uid', None)
        if iddep != None:
            sdep = SDepartment.objects.get(id=int(iddep))
            del data['id']
            try:
                del data['uid']
            except:
                pass
        elif uiddep != None:
            sdep = SDepartment.objects.get(uid=uiddep)
            del data['uid']
            try:
                del data['id']
            except:
                pass
        else:
            return JsonResponse({'errMsg': 'Ошибка в запросе'}, status=status.HTTP_400_BAD_REQUEST)

        sdep.jdata = data
        sdep.save()
        return JsonResponse({'report': 'Запись изменена'}, status=status.HTTP_204_NO_CONTENT)

    if request.method == 'DELETE':
        try:
            data = JSONParser().parse(request)
        except:
            data = request.data
        sdep = SDepartment.objects.get(id=int(data['id']))
        sdep.delete()

        return JsonResponse({'report': 'Запись удалена'}, status=status.HTTP_200_OK)
    return JsonResponse({'errMsg': 'Ошибка в запросе'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'GET', 'DELETE', 'POST'])
def s_person(request):
    try:
        if request.method == 'GET':
            idorg = request.GET.get('idorg', None)
            iddep = request.GET.get('iddep', None)
            idpos = request.GET.get('idpos', None)
            search = request.GET.get('query', None)

            if search != None and search.lower() != 'вакансия':
                 dop_filter = Q(name__icontains=search)
            else:
                dop_filter = Q()

            if idorg != None:
                dop_filter = dop_filter & Q(id_sorganization_id=int(idorg))
            if iddep != None:
                dop_filter = dop_filter & Q(id_sdepartment_id=int(iddep))
            if idpos != None:
                dop_filter = dop_filter & Q(id_sposition_id=int(idpos))

            spers = SPerson.objects.filter(dop_filter)[0:8]
            jlist = []
            for s in spers:
                j = {}
                jdata = s.jdata
                j.update({'id': s.id, 'uid': s.uid})
                try:
                    j.update({'org_name': s.id_sorganization.name})
                except:
                    pass

                try:
                    j.update({'dep_name': s.id_sdepartment.name})
                except:
                    pass

                try:
                    j.update({'pos_name': s.id_sposition.name})
                except:
                    pass
                j.update(jdata)
                jlist.append(j)

            if search == None and len(spers) != 1:
                return JsonResponse({"msg": "Кол-во сотрудников <> 1"}, safe=False, status=status.HTTP_200_OK)

            return JsonResponse(jlist, safe=False, status=status.HTTP_200_OK)

        if request.method == 'POST':
            try:
                data = JSONParser().parse(request)
            except:
                data = request.data
            spers = SPerson(jdata=data)
            spers.save()
            j = {}
            jdata = spers.jdata
            j.update({'id': spers.id, 'uid': spers.uid})
            j.update(jdata)
            return JsonResponse(j, status=status.HTTP_201_CREATED)

        if request.method == 'PUT':
            try:
                data = JSONParser().parse(request)
            except:
                data = request.data
            spers = SPerson.objects.get(id=int(data['id']))
            del data['id']
            spers.jdata = data
            spers.save()
            return JsonResponse(data, status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            try:
                data = JSONParser().parse(request)
            except:
                data = request.data
            spers = SPerson.objects.get(id=int(data['id']))
            spers.delete()

            return JsonResponse({'report': 'Запись удалена'}, status=status.HTTP_200_OK)
        return JsonResponse({'errMsg': 'Ошибка в запросе'}, status=status.HTTP_400_BAD_REQUEST)
    except:

        return JsonResponse({'errMsg': 'Ошибка в запросе'}, status=status.HTTP_400_BAD_REQUEST)


def get_jsdata(spers):
    jdata = {}
    try:
        jdata.update({'organization_name': spers.id_sorganization.name})
    except:
        pass
    try:
        jdata.update({'department_full_name': spers.id_sdepartment.name})
    except:
        pass
    try:
        jdata.update({'position_full_name': spers.id_sposition.name})
    except:
        pass

    return jdata


def data_set(uid=None):
    data = {}
    try:
        spers = Persons.objects.get(person_id=uid)
        pers = SPerson.objects.filter(uid=uid[0:20])
    except:
        return data

    iddep = None
    idorg = None
    idpers = None


    # Можно поставить условие для сравнения ДР
    # birthday = pers.jdata['birthday']
    # born = datetime.strptime(birthday, '%d.%m.%Y')
    if len(pers) > 0:
        fpers = pers.first()
        data = fpers.jdata
        data.update({"idpers":fpers.id})
        return data




    if spers.organization_name:
        org = SOrganization.objects.filter(name=spers.organization_name)
        if len(org) == 0:
            jdata = {"value": spers.organization_name}
            sorg = SOrganization(jdata=jdata)
            sorg.save()
            idorg = sorg.id
        else:
            idorg = org.first().id

    if spers.department_full_name and idorg:
        dep = SDepartment.objects.filter(name=spers.department_full_name, id_sorganization_id=idorg)
        if len(dep) == 0:
            jdata = {"value": spers.department_full_name, "shortValue": spers.department_short_name, "idorg":idorg }
            sdep = SDepartment(jdata=jdata)
            sdep.save()
            iddep = sdep.id
        else:
            iddep = dep.first().id

    if spers.position_critical == 'Да' or spers.position_critical == 'КВД':
        position_critical = 'Да'
    else:
        position_critical = 'Нет'

    if spers.position_full_name and iddep:
        pos = SPosition.objects.filter(name=spers.position_full_name, id_sdepartment_id=iddep)
    elif spers.position_full_name and idorg:
        pos = SPosition.objects.filter(name=spers.position_full_name, id_sorganization_id=idorg)
    else:
        pos = SPosition.objects.filter(name=spers.position_full_name)

    if len(pos) == 0:
        jdata = {"value": spers.position_full_name, "shortValue": spers.position_short_name,
                 "position_critical": position_critical, "idorg":idorg, "iddep":iddep }
        sdep = SPosition(jdata=jdata)
        sdep.save()
        idpos = sdep.id
    else:
        idpos = pos.first().id
    data = {"iddep": iddep, "idorg": idorg, "idpos": idpos}
    if spers.person_fio.lower() == 'вакансия':
        idpers = None
    else:
        if len(pers) == 0:
            jdata = PersonSerializer(spers).data
            jdata.update(data)
            npers = SPerson(jdata=jdata)
            npers.save()
            idpers = npers.id
            data.update({"idpers":idpers})
    # data.update(data_get(idorg, iddep, idpos, idpers))

    return data


@api_view(['GET'])
def s_create(request):
    if request.method == 'GET':
        try:
            uid = request.GET.get('uid', None)
            if uid != None:
                try:
                    spers = SPerson.objects.get(uid__istartswith=uid[0:20])
                    idorg = spers.id_sorganization
                    idpos = spers.id_sposition
                    iddep = spers.id_sdepartment
                    idpers = spers.id
                    return JsonResponse({"idorg": idorg, "idpos": idpos, "iddep": iddep, "idpers": idpers}, safe=False,
                                        status=status.HTTP_200_OK)
                except Exception as e:
                    return JsonResponse(data_set(uid), safe=False, status=status.HTTP_200_OK)

            else:
                return JsonResponse({'errMsg': 'Отсутствует UID в запросе'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return JsonResponse({'errMsg': 'Ошибка в запросе'}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
def s_person_get(request):
    try:
        uid = request.GET.get('uid', None)
        if uid != None:
            try:
                spers = SPerson.objects.get(uid__istartswith=uid[0:20])
                jdata = spers.jdata
                jdata.update(get_jsdata(spers))
            except Exception as e:
                spers = Persons.objects.get(person_id=uid)
                jdata = PersonSerializer(spers).data

            return JsonResponse(jdata, safe=False, status=status.HTTP_200_OK)

        if request.method == 'GET':
            id = request.GET['id']
            spers = SPerson.objects.get(id=int(id))
            jdata = spers.jdata
            jdata.update(get_jsdata(spers))

            return JsonResponse(jdata, safe=False, status=status.HTTP_200_OK)
    except:
        return JsonResponse({'errMsg': 'Ошибка в запросе'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def s_data_get(request):
    try:
        if request.method == 'GET':
            idorg = request.GET.get('organization', None)
            iddep = request.GET.get('department', None)
            idpos = request.GET.get('position', None)
            idpers = request.GET.get('person', None)
            data = data_get(idorg, iddep, idpos, idpers)

            return JsonResponse(data, safe=False, status=status.HTTP_200_OK)
    except:
        return JsonResponse({'errMsg': 'Ошибка в запросе'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def person_profile_get(request):
    uid = request.GET['uid']
    return JsonResponse(get_profile_jf(uid), safe=False, status=status.HTTP_200_OK)
@api_view(['GET', 'POST', 'PUT'])
def person_profile(request):
    try:
        if request.method == 'GET':
            uid = request.GET['uid']
            pf = Person_profile.objects.get(idperson__istartswith=uid[0:20])
            return JsonResponse(pf.jdata, safe=False, status=status.HTTP_200_OK)

        if request.method == 'POST':
            try:
                data = JSONParser().parse(request)
            except:
                data = request.data
            obj, created = Person_profile.objects.update_or_create(
                idperson__istartswith=data['idperson'][0:20],
                defaults={'jdata': data, 'idperson': data['idperson'][0:20], 'name': data['person_fio']},
            )

            return JsonResponse(obj.jdata, safe=False, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({'errMsg': 'Ошибка в запросе'}, status=status.HTTP_400_BAD_REQUEST)


class TPLRenderer(renderers.BaseRenderer):
    media_type = mimetypes.guess_type('aa.xlsx')
    format = 'xlsx'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


@api_view(['GET'])
# @renderer_classes([TPLRenderer])
def get_tpl(request):
    if request.method == 'GET':

        try:
            file = 'profile_tpl.xlsx'
            f = open(os.path.join(settings.MEDIA_ROOT, 'tpl', file), 'rb')

            response = HttpResponse(f, content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename="profile_tpl.xlsx"'
            return response
        except:
            pass

@api_view(['GET'])
# @renderer_classes([TPLRenderer])
def get_manual(request):
    if request.method == 'GET':

        try:
            file = 'manual.pdf'
            f = open(os.path.join(settings.MEDIA_ROOT, 'tpl', file), 'rb')

            response = HttpResponse(f, content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename="manual.pdf"'
            return response
        except:
            pass