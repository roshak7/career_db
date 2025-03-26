

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication


from rest_framework.permissions import IsAuthenticated

from career.math.alg1 import *
from career.math.alg3 import edges_correct
from career.upload.utils import ready



from datetime import datetime, date

from django.http.response import JsonResponse

from career.models import Career_data, Career_structure, Persons
from career.serializers import CareerSerializer, PersonSerializer
# import django
# import os

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings_base")
# django.setup()
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
        (синий) Должность полностью защищена: утверждены два преемника один из них почти готов (готовность не более 1 года)
        (зел) Должность защищена: утвержден один преемник (готовность не более 1 года)
        (жел) Должность частично защищена: утвержден один преемник (готовность более 1 года)
        (красн) Должность не защищена: преемники не утверждены

    Для 4-х видов добавится protect = 0 - это должен быть синий
    Для этого необходимо поставить условие suc_count > 1 и min(ready_list)==0
    '''
    if suc_count < 1:
        protect = 3
    else:
        if min(ready_list) <= 1:
            if min(ready_list) ==-1:
                protect = 3
            else:
                protect = 1
        else:
            protect = 2
    if suc_count > 1 and min(ready_list) == 0:
        protect = 0

    return protect
    # org_new = {'protect': protect, 'id': obj['id'], 'img': '/img/%s/' % person_boss.person_id_photo,
    #            'parentID': obj['parentID'],
    #            'x': 0, 'y': 0, 'w': WM}

def person_data(p_list:list, id:str):
    p_dict = {}
    for p in p_list:
        if p['person_id']==id:
            p_dict=p
            break
    return p_dict
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


# tes_succ()


def person_l(orgstr, orgsuc, org_name):
    p_list = []
    p_list_kvd = []
    persons_list = []
    persons_list_succ = []
    for org_s in orgstr:
        persons_list.append(org_s['id'])

    for org_suc in orgsuc:
        persons_list_succ.append(org_suc['id'])
    persons_list_all = persons_list + persons_list_succ
    # pers = Persons.objects.filter(person_id__in=persons_list_all)
    for pers in persons_list_all:
        try:
            p = Persons.objects.get(person_id=pers)
        except:
            continue
        data = PersonSerializer(p).data
        if p.person_id in persons_list:
            if p.position_critical=='Да':
                p_list_kvd.append(p.person_id)
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
        # data.update(({'organization_name': org_name}))
        p_list.append(data)
    return persons_list, p_list, p_list_kvd


@api_view(['GET'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def career_cards_view(request, pk):
    org_name=''
    id_map=''
    try:
        # Получаем объект с данными по карте id=pk
        cards_successor = Career_structure.objects.get(pk=pk)
        org_name = cards_successor.company
        # Получаем данными по должностям
        org_list = cards_successor.jdata_org_structure
        # Получаем данными по преемникам
        org_successor_list = cards_successor.jdata_org_successor
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
            id_map = '_'+str(pk)
        # расставляем координаты для созданной модели данных
        jdata = placement_coordinate(jdata)

        org_list = []
        org_succ = []
        x_max = 0
        boss_xmax = 0
        total_positions = 0
        total_successors = 0
        pr = [0, 0, 0, 0]
        readiness_l = [0, 0, 0, 0, 0, 0]
        x_boss = jdata[0]['boss'][0][0]
        for j in jdata:
            boss_xmax = max(boss_xmax, j['boss'][0][0])
            id_node = j['id']
            p_photo = 'none'
            try:
                p_d = person_data(p_list, id_node)
                # person = Persons.objects.get(person_id=id_node)
                p_photo = p_d['person_id_photo']+id_map
            except:
                pass
            # print(j)

            ready_list = []

            json_new = {"h": 105, "w": 400, "x": j['boss'][0][0],
                        "y": j['boss'][0][1], "id": j['id'],
                        'img': '/api/v1/img/%s/' % p_photo, "parentID": j['parentID']}
            try:
                json_new.update({'edges2': [[x_boss / 10 + 24.85, j['y1'] / 10 + 4.5],
                                            [j['boss'][0][0] / 10 + 24.85, j['y1'] / 10 + 4.5]]})
            except:
                pass

            if j['succ'] > 0:
                count_s = 0
                c_pos = 0
                for osl in org_successor_list:

                    s_photo = 'none'

                    if j['id'] == osl['parentID']:
                        c_pos +=1
                        if c_pos>4:
                            pos='l'
                        else:
                            pos='r'
                        try:
                            p_dict = person_data(p_list, osl['id'])
                            # person_s = Persons.objects.get(person_id=osl['id'])
                            readiness = p_dict['readiness']
                            ready_list.append(ready(readiness))
                            s_photo = p_dict['person_id_photo']+id_map
                        except:
                            pass
                            # print(readiness)
                        x, y = j['suxy'][count_s]
                        x_max = max(x_max, x)
                        org_succ.append({"w": 400, "x": x, "y": y,
                                         "id": osl['id'], 'img': '/api/v1/img/%s/' % s_photo,
                                         "parentID": osl['parentID'], "order_number": 1, 'pos':pos})
                        count_s += 1
            protect = protect_d(j['succ'], ready_list)
            pr[protect] += 1
            for n1 in ready_list:
                readiness_l[n1] += 1
            json_new.update({'protect': protect})
            org_list.append(json_new)
        total_positions = len(org_list)
        pr_dict = {}
        read_dict = {}
        for ip in range(0, len(pr)):
            pr_dict.update({"p%d" % ip: pr[ip]})
        for lp in range(0, len(readiness_l)):
            read_dict.update({"p%d" % lp: readiness_l[lp]})
        org_list.append({"id": 'organization', 'name': cards_successor.company, 'x': 0, 'y': 0})
        if x_max < boss_xmax:
            x_max = boss_xmax
        if len(jdata)>1:
            org_list.append({"id": 'legend', 'name': 'Легенда', 'x': x_max - 200, 'y': 0})
        else:
            org_list.append({"id": 'legend', 'name': 'Легенда', 'x': x_max + 200, 'y': 0})
        org_list = edges_correct(jdata, org_list)
        change_enabled = False # Отключаем загрузку сохраненных изменений
        if cards_successor.jdata_card_changes != None and change_enabled:
            for count, org in enumerate(org_list):
                id_node = org['id']
                for csl in cards_successor.jdata_card_changes:
                    try:
                        issuccessor = csl['data']['nodes'][0]['data']['isSuccessor']
                    except:
                        issuccessor = False

                    if csl['id'] == id_node and issuccessor == False:
                        # if csl['id'] == id_node and csl['data']['nodes'][0]['data']['isSuccessor'] == False:
                        try:
                            org_list[count].update({"x": csl['data']['nodes'][0]['position']['x'],
                                                    "y": csl['data']['nodes'][0]['position']['y']})
                        except:
                            pass

            for count, org2 in enumerate(org_successor_list):
                id_node = org2['id']

                for csl2 in cards_successor.jdata_card_changes:
                    try:
                        issuccessor = csl2['data']['nodes'][0]['data']['isSuccessor']
                    except:
                        issuccessor = False
                    # if csl2['id'] == id_node and csl2['data']['nodes'][0]['data']['isSuccessor'] == True:
                    if csl2['id'] == id_node and issuccessor == True:
                        org_succ[count].update({"x": csl2['data']['nodes'][0]['position']['x'],
                                                "y": csl2['data']['nodes'][0]['position']['y']})

        total_successors = len(org_succ)
        data = {"persons": p_list,
                "org_structure": org_list,
                "successor": org_succ,
                "changes": cards_successor.jdata_card_changes,
                "company": cards_successor.company,
                "card_name": cards_successor.name,
                "stat": {"total_positions": total_positions, "total_successors": total_successors, "protect": pr_dict,
                         "ready": read_dict, "total_critical": len(p_list_kvd)}
                }


    except Career_data.DoesNotExist:
        return JsonResponse({'message': 'Карта не найдена'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # cards_successor_serializer = CareerSerializer(cards_successor)
        return JsonResponse(data)  # , cards_successor_serializer.data
