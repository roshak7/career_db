import matplotlib.pyplot as plt

PW = 400
PH = 450
CONTUR_OBJ = 1
OTSTUP_V = 5
OTSTUP_H = 5
OTSTUP_HB = 10  # расстояние между блоками
DOLZH_HS = 10
DOLZH_WS = 40

DOLZH_HS_C = DOLZH_HS + (CONTUR_OBJ * 2)
DOLZH_WS_C = DOLZH_WS + (CONTUR_OBJ * 2)

SUCC_HS = 10
SUCC_WS = 40

SUCC_HS_C = SUCC_HS + (CONTUR_OBJ * 2)
SUCC_WS_C = SUCC_WS + (CONTUR_OBJ * 2)

OTSTUP_X = 5
OTSTUP_Y = DOLZH_HS * 2
Y_START = 30

JDATA = [{'id': 1, 'parentID': '', 'succ': 8},
         {'id': 13, 'parentID': 1, 'succ': 0},
         {'id': 2, 'parentID': 1, 'succ': 1},
         {'id': 3, 'parentID': 1, 'succ': 2},
         {'id': 4, 'parentID': 1, 'succ': 4},
         {'id': 5, 'parentID': 1, 'succ': 5},
         {'id': 6, 'parentID': 1, 'succ': 6},
         {'id': 7, 'parentID': 1, 'succ': 7},
         {'id': 8, 'parentID': 1, 'succ': 2},
         {'id': 9, 'parentID': 1, 'succ': 4},
         {'id': 10, 'parentID': 1, 'succ': 1},
         {'id': 11, 'parentID': 1, 'succ': 3},
         {'id': 12, 'parentID': 1, 'succ': 0},

         ]

def center_main(x,y, ws, hs, max_h):
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
        print(JDATA[i])
        max_h=jdata[i]['max_h']
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
            y1 = center_main(x,y,ws,hs,max_h)[1]
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
            for j in range(1, 5 if n['succ']>4 else n['succ']+1):
                # x1 = x
                succ_r.append([x1, y1])
                y1 = y1 + SUCC_HS_C

                y1 += OTSTUP_V
        if len(succ_l) > 0:
            succ_r = succ_r + succ_l
        jdata[i].update({'boss': boss, 'suxy':succ_r})

    #     x = n['x']
    #     y = n['y']
    #     ws = n['ws']
    #     hs = n['hs']
    #     max_h = n['max_h']
    #
    #     x2 = x + ws
    #     y2 = y + max_h
    #
    #     x3 = (x2 - x) / 2 + x
    #     y3 = (y2 - y) / 2 + y
    #     a1 = x3 - ws / 2
    #     a2 = x3 + ws / 2
    #     b2 = y3 + hs / 2
    #     b1 = y3 - hs / 2
    #
    #     jdata[i].update({'x': a1, 'y': b1})
    #     # print(jdata[i])
    #
    # return jdata


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


# высчитывает координаты преемников
# def center_objects2(jdata, l,r,c):
#
#
#         print(JDATA[i])
#         x = n['x']
#         y = n['y']
#         ws = n['ws']
#         hs = n['hs']
#         max_h = n['max_h']
#
#         x2 = x + ws
#         y2 = y + max_h
#
#         x3 = (x2 - x) / 2 + x
#         y3 = (y2 - y) / 2 + y
#         a1 = x3 - ws / 2
#         a2 = x3 + ws / 2
#         b2 = y3 + hs / 2
#         b1 = y3 - hs / 2
#
#         jdata[i].update({'x': a1, 'y': b1})
#         # print(jdata[i])
#
#     return jdata

def max_h_in_line(i1, i, max_h):
    for n in range(i1, i + 1):
        JDATA[n].update({'max_h': max_h})


def draw_rectangles():
    fig, ax = plt.subplots(figsize=(13, 10))
    ax.set_xlim(0, PW)  # Canvas width
    ax.set_ylim(0, PH)  # Canvas height
    plt.gca().invert_yaxis()

    x = 0  # Starting X-coordinate for the first rectangle
    y = Y_START
    # plt.axhline(y=y - OTSTUP_Y / 2, color='r', linestyle='-')

    JDATA[0].update(size_section(JDATA[0]))
    ws, hs = JDATA[0]['full_size']
    max_h = hs
    i1 = 0
    i2 = 0
    for i in range(len(JDATA)):
        # Draw rectangle
        i2 = i
        # ws, hs = size_section(JDATA[i])['full_size']
        JDATA[i].update(size_section(JDATA[i]))
        ws, hs = JDATA[i]['full_size']
        max_h = max(max_h, hs)
        JDATA[i].update({'y': y, 'x': x, 'ws': ws, 'hs': hs})

        x += ws + OTSTUP_HB

        # x += DOLZH_WS + OTSTUP_X  # Increment X-coordinate for the next rectangle with spacing
        if x + ws > PW or i == 0:
            max_h_in_line(i1, i2, max_h)
            i1 = i + 1
            x = 0

            y += max_h + OTSTUP_Y
            max_h = 0
            plt.plot([0, PW], [y - OTSTUP_Y / 2, y - OTSTUP_Y / 2])

    max_h_in_line(i1, i2, max_h)

    # jdata = center_objects(JDATA)

    center_elements(JDATA)
    for n in JDATA:
        # size_section(n)['full_size']
        for b in n['boss']:
            rectangle = plt.Rectangle((b[0], b[1]), DOLZH_WS_C, DOLZH_HS_C, fc='black', alpha=0.9)
            ax.add_patch(rectangle)
        for s in n['suxy']:
            rectangle = plt.Rectangle((s[0], s[1]), DOLZH_WS_C, DOLZH_HS_C, fc='black', alpha=0.4)
            ax.add_patch(rectangle)
        # for d in range(n['succ']):
        #     if d<1:
        #         pass
        #     if d>=1 and d<=4:
        #         pass
        #     if d>=5 and d<=8:
        #         pass


    # plt.axhline(y=y-50, color='b', linestyle=':')
    plt.gca().set_aspect('equal')  # Set aspect ratio to maintain rectangle proportions
    # plt.axis('off')  # Remove axis and ticks
    plt.show()


draw_rectangles()
