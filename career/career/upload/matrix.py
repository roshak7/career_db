from career.models import Career_structure, Persons
from career.upload.work_page import page_raspred

from career.upload.utils import *

def matrix(id=None):
    """
    Ширина блока руководителя WM
    Высота блока руководителя HM
    Ширина блока преемника WS
    Высота блока преемника HS
    Расстояние между блоком руководителя и одним преемником LMS
    Расстояние между блоками преемников если их более 2-х LSS
    Расстояние между блоками руководителей по вертикали без учета преемников LVM
    Расстояние между блоками руководителей по горизонтали без учета преемников LHM
    Верхняя левая точка координат (начальная) X, Y
    """

    # # WM = 400
    # HM = 105
    # WS = 400
    # HS = 100
    # LMS = 50
    # LSS = 30
    # LVM = 200
    # LHM = 40
    # X = 0
    # Y = 0
    Y2 = 0
    # A4 = 16
    # A3 = 25
    # A2 = 35
    # A1 = 45

    cs = Career_structure.objects.get(id=id)
    org_structure = cs.jdata_org_structure
    org_successor = cs.jdata_org_successor
    count = 0
    y = Y2 + HM + LVM
    y1 = 1
    x = X
    c2 = 0
    org_list = []
    suc_count_dict = {}
    num_list = []
    protect = 3
    k = 0
    data_cs = []
    for obj in org_structure:
        person_boss = Persons.objects.get(person_id=obj['id'])
        suc_count = 0
        objsc = {}
        data_cs_1 = {'c_id': obj['id'], 's_id': []}
        s_id = []
        ready_list = []
        for num, obj_suc in enumerate(org_successor):
            person = Persons.objects.get(person_id=obj_suc['id'])
            if obj_suc['parentID'] == obj['id']:
                s_id.append(obj_suc['id'])
                suc_count += 1
                ready_list.append(ready(person.readiness))
                objsc = {str(obj_suc['parentID']): suc_count}
                num_list.append(
                    {'num': num, 'obr': 0, 'order_number': suc_count, 'id': obj_suc['id'],
                     'img': '/api/v1/img/%s/' % person.person_id_photo,
                     'parentID': obj_suc['parentID'],
                     'x': 0, 'y': 0})
            suc_count_dict.update(objsc)
        data_cs_1.update({'s_id': s_id})
        data_cs.append(data_cs_1)
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
            if min(ready_list) == 0:
                protect = 1
            else:
                protect = 2
        if suc_count > 1 and min(ready_list) == 0:
            protect = 0

        org_new = {'protect': protect, 'id': obj['id'], 'img': '/api/v1/img/%s/' % person_boss.person_id_photo,
                   'parentID': obj['parentID'],
                   'x': 0, 'y': 0, 'w': WM}

        org_list.append(org_new)
    for obj in num_list:
        person_boss = Persons.objects.get(person_id=obj['id'])
        num = obj['num']
        id_obj = obj['id']
        parentid = obj['parentID']
        order_number = obj['order_number']
        org_successor[num] = {'id': id_obj, 'img': '/api/v1/img/%s/' % person_boss.person_id_photo,
                              'order_number': order_number, 'parentID': parentid, 'x': 0, 'y': 0, 'w': WM}

    aza = page_raspred(data_cs, org_list, org_successor)
    cs.jdata_org_structure = aza[0]
    cs.jdata_org_successor = aza[1]
    cs.save()



