from career.upload.utils import *

def page_line_matrix(data, org_list, org_succ):
    data_cs = data
    matrix_list = []

    end = True
    # page_size = A4_PX
    start_x = 0
    start_y = 0
    count_cs = len(data_cs)
    page = PAGES[0]
    wile_count = -1
    pr = False
    list_r = []  # для фиксации порядкового номера после которого происходит перевод на др строку
    count_in_line = 0  # кол-во объектов в строке
    ylist = []
    while end:
        for cc in range(0, count_cs):
            matrix_list.append([0.0, 0.0, 0, 0])
        wile_count += 1
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
        h_max_list = []

        x = start_x
        y = start_y
        num_data = 0
        h_list = []
        ylist = []

        for num_data, cs_one in enumerate(data_cs):

            pr = False
            count_in_line += 1
            count_cs_pp += 1

            count_r_s = 0
            count_s = len(cs_one['s_id'])  # кол-во блоков преемника

            if count_s <= 4:  # кол-во блоков справа, если общее кол-во преемников >4 то оставляем справа 4
                count_r_s = count_s
                w_max = LMS + WS + WM
                if count_s == 0:
                    w_max = LMS + WM
            else:
                count_r_s = 4
                w_max = 2 * (LMS + WS) + WM

            w_sum = w_sum + w_max
            h_s = (HS + LSS) * count_r_s  # вычисляем общуую высоту блоков преемников справа
            h_max = max(h_s, HM, h_max)  # вычисляем максимальное значение высоты блока должности с преемниками
            # h_max_list.append(h_max)
            # print(cs_one, count_s, count_r_s, h_s, h_max)
            h_s = 0

            matrix_list[num_data] = [w_max, h_max, 0, h_sum]

            if w_sum > page[1]:  # сравниваем ширину строки с шириной листа
                matrix_list[num_data - 1][2] = 1
                # print(matrix_list[num_data-1][2])
                h_sum += h_max

                # print('достигнута максимальная ширина листа на %s px' % str(w_sum - page[1]), page[1], y)
                pr = True

                if y > page[0]:
                    # print('достигнута максимальная высота листа на %s px' % str(y - page[0]))
                    list_r = []
                    break
            else:
                w_sum += LHM

            if count_cs_pp == 1:  # условие при котором переводим объекты на новую строку (для верхнего уровня)

                w_sum = 0
                y = y + h_max + RML

                x = start_x
                count_in_line = 0
                h_max = LVM + HM
                matrix_list[num_data] = [w_max, h_max, 1]
                h_list.append(y)
                # print(y)
                # data_cs[num_data].update({"ymax":y})
                # pr = True
                # print('прошли 1-ю линию %s px' % str(w_sum - page[1]), page[1], y)
                # h_sum = h_sum + h_max

            if pr == True:  # условие при котором переводим на др линию
                # list_r.append(
                #     {'number_line': num_data, 'h_max': h_max, 'count_in_line': count_in_line})
                count_in_line = 0
                w_sum = w_max

                y = y + h_max + RML
                x = start_x
                h_max = LVM + HM
                h_list.append(y)

            ylist.append(y)

            if count_cs_pp > 100:
                break

            # for ss_one in cs_one['s_id']:
            #
            #     print(ss_one)

        if num_data + 1 == count_cs:
            # list_r.append({'number_line': num_data, 'h_max': h_max, 'count_in_line': count_in_line})
            count_in_line = 0
            # print(num_data)
            end = False
        list_r = []
        count_in_line = 0
        for num_data, cs_one in enumerate(data_cs):

            count_in_line += 1
            if matrix_list[num_data][2] == 1:
                list_r.append(
                    {'number_line': num_data, 'h_max': matrix_list[num_data][1], 'count_in_line': count_in_line,
                     'h_sum': h_list})
                count_in_line = 0
            if num_data + 1 == count_cs:
                list_r.append(
                    {'number_line': num_data, 'h_max': matrix_list[num_data][1], 'count_in_line': count_in_line,
                     'h_sum': h_list})
        # list_r.append(
        #     {'number_line': 100, 'h_max': 100, 'count_in_line': 100, 'h_sum': y})
        # print(y, h_sum)
    # print(list_r)
    for num_data, cs_one in enumerate(data_cs):
        data_cs[num_data].update({"ymax": ylist[num_data]})
    return [list_r, page, data_cs]

def page_raspred(data, org_list, org_succ):
    # data_cs = data
    # end = True
    # page_size = A4_PX
    start_x = 0
    start_y = 0

    plm = page_line_matrix(data, org_list, org_succ)
    list_r = plm[0]
    page = plm[1]
    data_cs = plm[2]
    all_count = 0  # порядковый номер должности
    x = start_x
    y = start_y
    new_org = org_list
    for cn, norg in enumerate(new_org):
        # print(new_org[cn], data_cs[cn]['c_id'], data_cs[cn]['ymax'])
        new_org[cn].update({'ymax':data_cs[cn]['ymax']})

    new_org_succ = org_succ
    for n, lr in enumerate(list_r):  # n номер линии от 0
        number_line = lr['number_line']
        count_in_line = lr['count_in_line']
        h_max = lr['h_max']
        # print(data_cs[all_count])
        # print(lr, n+1)
        # lb = False
        # rb = False

        for nod_in_l in range(0, count_in_line):
            lb = False
            rb = False
            c_id = data_cs[all_count]['c_id']
            ymax = data_cs[all_count]['ymax']
            s_kol = len(data_cs[all_count]['s_id'])  # кол-во преемников
            if s_kol > 4:
                s_kol_r = 4
            else:
                s_kol_r = s_kol
            y1 = y
            if number_line == 0:
                x = page[1] / 2 - WS / 2 + RML + LHM/2 - 60
                y1 = y1 - s_kol_r *(HS)/2

                if s_kol_r == 1:
                    x = page[1] / 2 - WS*2 + 150
                    y1 = y1 - s_kol_r * (HS) / 2
            # вычисляем кооррдинаты блока слева от должности
            for lblock in range(4, s_kol):
                s_id = data_cs[all_count]['s_id'][lblock]
                lb = True
                xy_l = xy_ret(s_kol, HS, lblock + 1, h_max, x, y1)
                new_org_succ = change_org_succ_xy(new_org_succ, s_id, xy_l[0], xy_l[1])
                # print('left', xy_l)
                x = xy_l[0]
                y1 = xy_l[1] + HS + LSS
            if lb == True:
                x = x + WS + LMS
                y1 = y
            # вычисляем кооррдинаты должности

            boss_xy = xy_ret(1, HM, 1, h_max, x, y1)
            new_org = change_org_xy(new_org, c_id, boss_xy[0], boss_xy[1], list_r)
            # print('boss', boss_xy)
            # вычисляем кооррдинаты блока справа от должности
            x = boss_xy[0] + WM + LMS
            yy1 = y1
            if number_line != 0:

                    if s_kol_r==3:
                        yy1=y1+ HS + HS/2-20
                    if s_kol_r==4:
                        yy1=y1 + HS*2 - HS/2
            for rblock in range(0, s_kol_r):
                s_id = data_cs[all_count]['s_id'][rblock]
                rb = True
                xy_r = xy_ret_s(s_kol, HS, rblock + 1, h_max, x, yy1)
                # print('right', xy_r)
                new_org_succ = change_org_succ_xy(new_org_succ, s_id, xy_r[0], xy_r[1])
                x = xy_r[0]
                if s_kol_r<=2:
                    yy1 = xy_r[1] + HS + LSS
            if rb == True:
                x = x + WS + LMS
            x = x + LHM

            # print(nod_in_l, all_count)

            if number_line == all_count:
                y = y + h_max + LHM
                x = start_x
            # if n == 0:
            #     x = start_x
            all_count += 1
    return [new_org, new_org_succ]


def xy_ret(all_line=0, height_node=0, current_line=0, h_max=0, x=0, y=0):
    k = all_line  # кол-во нод по вертикали
    if k>2:
        hml = h_max / k + LSS*k  # высчитываем размер одной лини от максимального размера
    else:
        hml = h_max / k
    hs1 = hml / 2  # середина высоты секции для вывода в линию
    hm_2 = height_node / 2  # половина высоты ноды должности
    # нач координаты
    x1 = x
    if k > 2:
        y1 = y - ((height_node)*k)/2 +LMS + (height_node+LSS)*(current_line-1)
    else:
        y1 = y + hs1 - hm_2
    return ([x1, y1])
    # тут надо записать координаты в массив

def xy_ret_s(all_line=0, height_node=0, current_line=0, h_max=0, x=0, y=0):
    k = all_line  # кол-во нод по вертикали
    if k>2:
        hml = h_max / k + LSS*k  # высчитываем размер одной лини от максимального размера
    else:
        hml = h_max / k
    hs1 = hml / 2  # середина высоты секции для вывода в линию
    hm_2 = height_node / 2  # половина высоты ноды должности
    # нач координаты
    x1 = x
    if k > 2:
        y1 = y - ((height_node)*k)/2 +LMS + (height_node+LSS)*(current_line-1)
    else:
        y1 = y + hs1 - hm_2

    # if all_line == 1:
    #     y1+=100
    # if all_line == 2:
    #     y1 += 200
    #
    # if all_line == 3:
    #     y1 += 300
    #
    # if all_line == 4:
    #     y1 += 400

    return ([x1, y1])
def change_org_xy(org_list, id, x, y, lr):
    items = []
    elem = {}
    i = 0
    for org in org_list:
        elem['id'] = org['id']
        elem['protect'] = org['protect']
        elem['parentID'] = org['parentID']
        elem['img'] = org['img']
        elem['w'] = org['w']
        elem['lr'] = lr
        elem['ymax'] = org['ymax']
        if org['id'] == id:
            elem['x'] = x
            elem['y'] = y

        else:
            elem['x'] = org['x']
            elem['y'] = org['y']
        # i = + 1

        items.append(elem)
        elem = {}
    return items


def change_org_succ_xy(org_list, id, x, y):
    items = []
    elem = {}
    i = 0
    for org in org_list:
        elem['id'] = org['id']
        elem['order_number'] = org['order_number']
        elem['parentID'] = org['parentID']
        elem['w'] = org['w']
        elem['img'] = org['img']
        if org['id'] == id:
            elem['x'] = x
            elem['y'] = y

        else:
            elem['x'] = org['x']
            elem['y'] = org['y']
        #     except:
        #         elem['x'] = 0
        #         elem['y'] = 0
        # i = + 1
        items.append(elem)
        elem = {}
    return items
