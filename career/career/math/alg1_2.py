DPI = 300
A4_SM = [21, 29.7]  # формат А4 в см
IN = 2.54  # см в 1 дюйме
A4_IN = [A4_SM[0] / IN, A4_SM[1] / IN]  # формат А4 в дюймах
A4_PX = [A4_IN[0] * DPI, A4_IN[1] * DPI]  # формат А4 в пикселях согласно DPI
A5_PX = [A4_PX[1] / 2, A4_PX[0]]  # формат А4 в пикселях согласно DPI
A3_PX = [A4_PX[1], A4_PX[0] * 2]  # формат А3 в пикселях
A2_PX = [A3_PX[1], A3_PX[0] * 2]  # формат А2 в пикселях
A1_PX = [A2_PX[1], A2_PX[0] * 2]  # формат А1 в пикселях
A0_PX = [A1_PX[1], A1_PX[0] * 2]  # формат А0 в пикселях
PAGES = [A5_PX, A4_PX, A3_PX, A2_PX, A1_PX, A0_PX]

PW = A3_PX[0]
PH = A3_PX[1]
CONTUR_OBJ = 1
CONTUR_S_OBJ = 2
OTSTUP_V = 5 #40
OTSTUP_H = 40 #80
OTSTUP_HB = 50  # 90 расстояние между блоками
DOLZH_HS = 131.5 # 100
DOLZH_WS = 340 #400

DOLZH_HS_C = DOLZH_HS + (CONTUR_OBJ * 2)
DOLZH_WS_C = DOLZH_WS + (CONTUR_OBJ * 2)

SUCC_HS = 109.5 #108
SUCC_WS = 340 #400

SUCC_HS_C = SUCC_HS + (CONTUR_S_OBJ * 2)
SUCC_WS_C = SUCC_WS + (CONTUR_S_OBJ * 2)

OTSTUP_X = 5 #5
OTSTUP_Y = DOLZH_HS/2.6
Y_START = 120 #120


def center_main(x, y, ws, hs, max_h):
    x2 = x + ws
    y2 = y + max_h

    x3 = (x2 - x) / 2 + x
    y3 = (y2 - y) / 2 + y
    a1 = x3 - ws / 2
    # a2 = x3 + ws / 2
    # b2 = y3 + hs / 2
    b1 = y3 - hs / 2
    return [a1, b1]


def center_elements(jdata):
    for i, n in enumerate(jdata):
        # print(jdata[i])
        max_h = jdata[i]['max_h']
        x = jdata[i]['x']
        y = jdata[i]['y']
        x1 = x
        succ_l = []
        succ_r = []
        l_size = jdata[i]['l_size']
        c_size = jdata[i]['c_size']
        r_size = jdata[i]['r_size']
        if n['succ'] >= 5:

            ws = l_size[0]
            hs = l_size[1]
            y1 = center_main(x, y, ws, hs, max_h)[1]
            for j in range(5, n['succ'] + 1):
                succ_l.append([x1, y1])
                y1 = y1 + SUCC_HS_C
                y1 += OTSTUP_V

            x1 += SUCC_WS_C + OTSTUP_H
        boss = []
        ws = c_size[0]
        hs = c_size[1]
        y1 = center_main(x1, y, ws, hs, max_h)[1]
        boss.append([x1, y1])

        if n['succ'] > 0:

            ws = r_size[0]
            hs = r_size[1]
            x1 += OTSTUP_H + ws
            # y1=y1 - hs  # нужно центрировать
            y1 = center_main(x1, y, ws, hs, max_h)[1]
            for j in range(1, 5 if n['succ'] > 4 else n['succ'] + 1):
                # x1 = x
                succ_r.append([x1, y1])
                y1 = y1 + SUCC_HS_C

                y1 += OTSTUP_V
        if len(succ_l) > 0:
            succ_r = succ_r + succ_l
        jdata[i].update({'boss': boss, 'suxy': succ_r})

    return jdata


# ф-я подсчета размера секций
def size_section(section: dict):
    size_w_1 = DOLZH_WS_C
    size_w_2 = DOLZH_WS_C + OTSTUP_H + SUCC_WS_C
    size_w_3 = SUCC_WS_C + OTSTUP_H + DOLZH_WS_C + OTSTUP_H + SUCC_WS_C

    size_h_1 = DOLZH_HS_C
    size_h_11 = SUCC_HS_C
    size_h_2 = SUCC_HS_C * 2 + OTSTUP_V
    size_h_3 = SUCC_HS_C * 3 + OTSTUP_V * 2
    size_h_4 = SUCC_HS_C * 4 + OTSTUP_V * 3

    size_succ1 = [SUCC_WS_C, SUCC_HS_C]
    size_succ2 = [SUCC_WS_C, SUCC_HS_C * 2 + OTSTUP_V]
    size_succ3 = [SUCC_WS_C, SUCC_HS_C * 3 + OTSTUP_V * 2]
    size_succ4 = [SUCC_WS_C, SUCC_HS_C * 4 + OTSTUP_V * 3]
    size = {}
    if section['succ'] == 0:
        # size = size_w_1, size_h_1
        size = {'full_size': [size_w_1, size_h_1], 'l_size': [], 'c_size': [size_w_1, size_h_1], 'r_size': []}
    if section['succ'] == 1:
        # size = size_w_2, max(size_h_1, size_h_11)
        size = {'full_size': [size_w_2, max(size_h_1, size_h_11)], 'l_size': [], 'c_size': [size_w_1, size_h_1],
                'r_size': size_succ1}

    if section['succ'] == 2:
        # size = size_w_2, size_h_2
        size = {'full_size': [size_w_2, size_h_2], 'l_size': [], 'c_size': [size_w_1, size_h_1],
                'r_size': size_succ2}

    if section['succ'] == 3:
        size = {'full_size': [size_w_2, size_h_3], 'l_size': [], 'c_size': [size_w_1, size_h_1],
                'r_size': size_succ3}

    if section['succ'] == 4:
        size = {'full_size': [size_w_2, size_h_4], 'l_size': [], 'c_size': [size_w_1, size_h_1],
                'r_size': size_succ4}

    if section['succ'] == 5:
        size = {'full_size': [size_w_3, size_h_4], 'l_size': size_succ1, 'c_size': [size_w_1, size_h_1],
                'r_size': size_succ4}

    if section['succ'] == 6:
        size = {'full_size': [size_w_3, size_h_4], 'l_size': size_succ2, 'c_size': [size_w_1, size_h_1],
                'r_size': size_succ4}

    if section['succ'] == 7:
        size = {'full_size': [size_w_3, size_h_4], 'l_size': size_succ3, 'c_size': [size_w_1, size_h_1],
                'r_size': size_succ4}

    if section['succ'] == 8:
        size = {'full_size': [size_w_3, size_h_4], 'l_size': size_succ4, 'c_size': [size_w_1, size_h_1],
                'r_size': size_succ4}

    return size


# высчитывает координаты преемников
def center_objects(jdata):
    for i, n in enumerate(jdata):
        # print(JDATA[i])
        x = n['x']
        y = n['y']
        ws = n['ws']
        hs = n['hs']
        max_h = n['max_h']

        x2 = x + ws
        y2 = y + max_h

        x3 = (x2 - x) / 2 + x
        y3 = (y2 - y) / 2 + y
        a1 = x3 - ws / 2
        a2 = x3 + ws / 2
        b2 = y3 + hs / 2
        b1 = y3 - hs / 2

        jdata[i].update({'x': a1, 'y': b1})
        # print(jdata[i])

    return jdata


def max_h_in_line(i1, i, max_h, jdata):
    for n in range(i1, i + 1):
        jdata[n].update({'max_h': max_h})
    return jdata


def placement_coordinate(jdata):
    jdata[0].update(size_section(jdata[0]))
    ws, hs = jdata[0]['full_size']
    max_h = hs
    pg = 0
    pw = PAGES[pg]
    end = True
    try:
        lsize = jdata[0]['l_size'][0]
    except:
        lsize = 0

    try:
        succ_1 = jdata[0]['succ']
    except:
        succ_1 = 0

    while end:
        x = 0  # Starting X-coordinate for the first rectangle
        y = Y_START
        if lsize > 0 or succ_1<=1:
            y = y + 80

        i1 = 0
        i2 = 0
        x1 = 0
        for i in range(len(jdata)):
            # Draw rectangle
            i2 = i
            # ws, hs = size_section(JDATA[i])['full_size']
            jdata[i].update(size_section(jdata[i]))
            ws, hs = jdata[i]['full_size']
            max_h = max(max_h, hs)
            jdata[i].update({'y': y, 'x': x, 'ws': ws, 'hs': hs})

            x += ws + OTSTUP_HB

            if i > 0:
                jdata[i].update({'y1': y - OTSTUP_Y / 2})

            if x + ws > pw[1] or i == 0:
                jdata = max_h_in_line(i1, i2, max_h, jdata)
                i1 = i + 1
                x = 0
                y += max_h + OTSTUP_Y
                max_h = 0

            jdata = max_h_in_line(i1, i2, max_h, jdata)
        if y > pw[0]:
            pg += 1
            pw = PAGES[pg]
        else:
            end = False
    # назначаем координату X для первой ноды


    if lsize > 0:

        if len(jdata)>1:
            jdata[0]['x'] = jdata[1]['x'] + jdata[1]['full_size'][0] - 10 - SUCC_WS_C - DOLZH_WS / 2 - OTSTUP_H / 2 - 20
        else:
            jdata[0]['x'] = 700
            jdata[0]['y'] = jdata[0]['y'] + 100
        # jdata[0]['y'] = jdata[0]['y'] + 100
    else:

        try:
            if jdata[1]['full_size'][0]<500:
                jdata[0]['x'] = jdata[0]['x'] + jdata[1]['full_size'][0] - DOLZH_WS / 2 + OTSTUP_H / 2 + 3
            else:
                jdata[0]['x'] = jdata[0]['x'] + jdata[1]['full_size'][0] - DOLZH_WS / 2 + OTSTUP_H / 2 + 3#- 29.5
        except:
            jdata[0]['x']=800
            jdata[0]['y']=jdata[0]['y']+100

    # if rsize <= 1:
    #     jdata[0]['y'] = jdata[0]['y'] + 100
    # центрируем объекты по высоте ряда где они расположены
    jdata = center_elements(jdata)

    return jdata
