from datetime import date, datetime

# from career.models import Career_structure

DPI = 300
A4_SM = [21, 29.7]  # формат А4 в см
IN = 2.54  # см в 1 дюйме
A4_IN = [A4_SM[0] / IN, A4_SM[1] / IN]  # формат А4 в дюймах
A4_PX = [A4_IN[0] * DPI, A4_IN[1] * DPI]  # формат А4 в пикселях согласно DPI
A3_PX = [A4_PX[1], A4_PX[0] * 2]  # формат А3 в пикселях
A2_PX = [A3_PX[1], A3_PX[0] * 2]  # формат А2 в пикселях
A1_PX = [A2_PX[1], A2_PX[0] * 2]  # формат А1 в пикселях
PAGES = [A4_PX, A3_PX, A2_PX, A1_PX]

WM = 400  # Ширина блока должности в px
HM = 100  # Высота блока должности в px
WS = 400  # Ширина блока преемника в px
HS = 100  # Высота блока преемника в px
LMS = 50  # Расстояние между блоком должности и одним преемником
LSS = 30  # Расстояние между блоками преемников если их более 2-х
LVM = 200  # Расстояние между блоками должностей по вертикали без учета преемников
LHM = 40  # Расстояние между блоками руководителей по горизонтали без учета преемников
RML = 100  # Расстояние между линиями уровней

X = 0  # Верхняя левая точка координат (начальная) X
Y = 0  # Верхняя левая точка координат (начальная) Y
Y2 = 0
A4 = 16
A3 = 25
A2 = 35
A1 = 45

def matrix_new(id=None):
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



    data_cs = [{'c_id':123, 's_id':[111,222,333]}, {'c_id':823, 's_id':[313]}, {'c_id':124, 's_id':[554,555]}, {'c_id':125, 's_id':[777,553,131,122,433]}, {'c_id':115, 's_id':[799,993,777,553,131,122,433]}]

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
    for obj in org_structure:
        suc_count = 0
        objsc = {}

        for num, obj_suc in enumerate(org_successor):
            if obj_suc['parentID'] == obj['id']:
                suc_count += 1
                objsc = {str(obj_suc['parentID']): suc_count}
                num_list.append(
                    {'num': num, 'obr':0, 'order_number': suc_count, 'id': obj_suc['id'], 'parentID': obj_suc['parentID'],
                     'x': 0, 'y': 0})
            suc_count_dict.update(objsc)

        if suc_count > 2:
            protect = 1
        if suc_count <= 2:
            protect = 2
        if suc_count < 1:
            protect = 3

        if obj['parentID'] == None or obj['parentID'] == '':
            org_new = {'protect': protect, 'id': obj['id'], 'parentID': obj['parentID'], 'x': X + WM/2 + WS + LMS/2 + LHM/2,
                       'y': Y, 'w': WM}
        else:
            # тут прописываем координаты для нижестоящих должностей
            count += 1


            if count % 4 != 0:

                x = X + (WM + WS + LMS + LHM) * c2 + k
                c2 += 1
                org_new = {'protect': protect, 'id': obj['id'], 'parentID': obj['parentID'], 'x': x, 'y': y,
                           'w': WM}
            else:
                x = X + (WM + WS + LMS + LHM) * c2 + k
                org_new = {'protect': protect, 'id': obj['id'], 'parentID': obj['parentID'], 'x': x, 'y': y,
                           'w': WM}
                y1 += 1
                c2 = 0
                y = Y2 + (HM + LVM) * y1

            if suc_count < 1:
                k = -1 * (WM)
            else:
                k = 0

        org_list.append(org_new)
    cs.jdata_org_structure = org_list
    cs.save()

    for obj in num_list:
        num = obj['num']
        parentid = obj['parentID']
        id = obj['id']
        order_number = obj['order_number']
        x_1 = 0
        y_1 = 0
        # cc = suc_count_dict[parentid]
        for c_1, org_1 in enumerate(org_list):
            if org_1['id'] == parentid:
                x_1 = org_1['x']
                y_1 = org_1['y']
                break
        x = x_1 + 450
        y = y_1
        col = suc_count_dict[parentid]
        y22=0
        if col > 1:
            if order_number == 1:
                y22 = y - ((HS - LSS) * col) / 2
            if order_number == 2:
                y22 = y + ((HS - LSS) * col) / 2

            if order_number == 3:
                y22 = y + ((HS - LSS) * col) / 3
            org_successor[num] = {'id': id, 'order_number': order_number, 'parentID': parentid, 'x': x,
                                   'y': y22, 'w': WM - 50}
        else:
            # if obj['obr'] == 0:
            org_successor[num] = {'id': id, 'order_number': order_number, 'parentID': parentid, 'x': x, 'y': y,
                                    'w': WM - 50}


    cs.jdata_org_structure = org_list
    cs.jdata_org_successor = org_successor
    cs.save()


# HS = 100
# LSS = 30
def page_raspred(data_cs=[]):
    # data_cs = [{'c_id':123, 's_id':[111,222,333]},{'c_id':76893, 's_id':[]},  {'c_id':823, 's_id':[313]}, {'c_id':124, 's_id':[554,555]}, {'c_id':125, 's_id':[777,553,131,122,433]}, {'c_id':115, 's_id':[799,993,777,553,131,122,433]},
    #            {'c_id':123, 's_id':[111,222,333]},{'c_id':76893, 's_id':[]},  {'c_id':823, 's_id':[313]}, {'c_id':124, 's_id':[554,555]}, {'c_id':125, 's_id':[777,553,131,122,433]}, {'c_id':115, 's_id':[799,993,777,553,131,122,433]},
    #            {'c_id':123, 's_id':[111,222,333]},{'c_id':76893, 's_id':[]},  {'c_id':823, 's_id':[313]}, {'c_id':124, 's_id':[554,555]}, {'c_id':125, 's_id':[777,553,131,122,433]}]
    data_cs=data_cs
    end = True
    page_size = A4_PX
    start_x = 0
    start_y = 0
    count_cs = len(data_cs)
    wile_count = -1
    pr = False
    list_r = [] # для фиксации порядкового номера после которого происходит перевод на др строку
    count_in_line = 0  # кол-во объектов в строке
    while end:

        wile_count+=1
        try:
            page = PAGES[wile_count]
        except:
            print('Ошибка в выборе формата листа')
            break
        count_cs_pp = 0  # счетчик кол-ва объектов должность
        w_sum = 0  # суммарная ширина тек. линии
        h_sum = 0  # суммарная высота линиий
        w_max = 0
        h_max = 0
        x = start_x
        y = start_y
        num_data = 0

        for num_data, cs_one in enumerate(data_cs):
            pr = False
            count_in_line += 1
            count_cs_pp += 1

            count_r_s = 0
            count_s = len(cs_one['s_id'])  # кол-во блоков преемника

            if count_s <= 4: # кол-во блоков справа, если общее кол-во преемников >4 то оставляем справа 4
                count_r_s = count_s
                w_max = LMS + WS + WM
            else:
                count_r_s = 4
                w_max = 2 * (LMS + WS) + WM


            w_sum = w_sum + w_max
            h_s = (HS + LSS) * count_r_s - LSS  # вычисляем общуую высоту блоков преемников справа
            h_max = max(h_s, HM, h_max)  # вычисляем максимальное значение высоты блока должности с преемниками
            # print(cs_one, count_s, count_r_s, h_s, h_max)
            h_s = 0
            if w_sum > page[1]:     # сравниваем ширину строки с шириной листа


                h_sum+=h_max

                # print('достигнута максимальная ширина листа на %s px' % str(w_sum - page[1]), page[1], y)
                pr = True
                w_sum = 0
                if y > page[0]:
                    # print('достигнута максимальная высота листа на %s px' % str(y - page[0]))
                    list_r = []
                    break
            else:
                w_sum+=LHM



            if count_cs_pp == 1:  # условие при котором переводим объекты на новую строку (для верхнего уровня)

                pr = True
                # print('прошли 1-ю линию %s px' % str(w_sum - page[1]), page[1], y)
                # h_sum = h_sum + h_max

            if pr == True: # условие при котором переводим на др линию
                list_r.append({'number_line':num_data, 'h_max':h_max, 'count_in_line':count_in_line})
                count_in_line = 0




                y = y + h_max + RML
                x = start_x

            if count_cs_pp > 100:
                break


            # for ss_one in cs_one['s_id']:
            #
            #     print(ss_one)
        if num_data +1 == count_cs:
            list_r.append({'number_line': num_data, 'h_max': h_max, 'count_in_line': count_in_line})
            count_in_line = 0
            # print(num_data)
            end=False


    all_count = 0  # порядковый номер должности
    for n,lr in enumerate(list_r):  # n номер линии от 0
        number_line = lr['number_line']
        count_in_line = lr['count_in_line']

        print(lr, n+1)
        for nod_in_l in range(0, count_in_line):

            print(nod_in_l, all_count)
            print(data_cs[all_count])
            all_count += 1


def xy_ret(all_line=0, height_node=0, current_line=0, x=0, y=0):
    k = all_line  # кол-во нод по вертикали
    hml = h_max / k  # высчитываем размер одной лини от максимального размера
    hs1 = hml / 2  # середина высоты секции для вывода в линию
    hm_2 = height_node / 2  # половина высоты ноды должности
    # нач координаты
    x1 = x
    y1 = y + hs1 - hm_2
    return ([x1,y1])
    # тут надо записать координаты в массив

'''
#############################
# расчет для ноды должности #
#############################
k = 1  # кол-во нод по вертикали
hml = h_max/k
hs1 = hml/2  # середина высоты секции для вывода в линию
hm_2 = HM / 2  # половина высоты ноды должности
# нач координаты
x1 = x
y1 = y + hs1 - hm_2
# тут надо записать координаты в массив


##############################
# расчет для ноды преемников #
##############################
if count_s <=4 and count_s > 0:
    k = count_s  # кол-во нод по вертикали
    hml = h_max / k
    hs1 = hml / 2  # середина высоты секции для вывода в линию
    hm_2 = HS / 2  # половина высоты ноды должности
        # for k1, o1 in enumerate(data_cs[num_data]['s_id']):
        #     pass

    # Нач. координаты
    x1 = x
    y1 = y + hs1 - hm_2


'''

