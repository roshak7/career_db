def line_add_to_position(obj: dict, number: int, lenorg):
    w = obj['w']

    # try:
    # print(obj['lr'])
    # except:
    # pass
    try:
        h = obj['h']
    except:
        h = 105
    line_v = 10
    x1 = w / 2
    y1 = 0 + h / 2
    x2 = x1
    y2 = h
    x3 = x2
    y3 = x3
    if number == 0:
        top = 0
    else:
        top = -1 * h
    left = 0

    sdvig = 900
    kx = 1000

    obj.update(
        {'line_coordinate': [[x1, y1], [x2, y2]], 'top': top, 'left': left})
    try:
        for ob in obj['lr']:
            # print(ob)
            h_max = ob['h_max']
            # y1 = h_max + y1
            k = h_max / 2
            if k < h:
                k = h
            y2 = k
            top = -1 * k
            if ob['number_line'] - ob['count_in_line'] == number - 1:
                if lenorg >= 12:
                    kx-=100
                # print('TOP', top, 'hmax',h_max )
                if ob['number_line'] == 0:
                    top = -1 * h
                    # print(top, y2)
                    h_sum = ob['h_sum'][-1]
                    if len(ob['h_sum']) == 3:
                        obj.update({'line_coordinate': [[x1, y2 + h + 15], [x2, y2 + h + 15 + h_sum - 386]], 'top': top,
                                    'left': left})
                    if len(ob['h_sum']) == 4:
                        if lenorg < 12:
                            obj.update({'line_coordinate': [[x1, y2 + h + 15], [x2, y2 + h + 15 + h_sum - 424.5],
                                                            [x2, y2 + h + 15 + h_sum - 424.5],
                                                            [x2 - 200, y2 + h + 15 + h_sum - 424.5]], 'top': top,
                                        'left': left})
                        elif lenorg >= 12:
                            k2=223
                            obj.update({'line_coordinate': [[x1, y2 + h + 15], [x2, y2 + h + 15 + h_sum - 424.5+k2],
                                                            [x2, y2 + h + 15 + h_sum - 424.5+k2],
                                                            [x2 - 200, y2 + h + 15 + h_sum - 424.5+k2]], 'top': top,
                                        'left': left})
                else:
                    obj.update({'line_coordinate': [[x1, y1], [x1, y2], [x1, y1], [x1 + kx, y1]], 'top': top})


            elif ob['number_line'] == number:
                obj.update(
                    {'line_coordinate': [[x1, y1], [x2 + kx - 200, y1], [x2 + kx - 200, y1], [x2 + kx - 200, y2]],
                     'top': top, 'left': left - kx + 200})
                # print('равенство', number)
            elif ob['number_line'] - ob['count_in_line'] < number:
                obj.update(
                    {'line_coordinate': [[x1, y1], [x1, y2], [x1, y1], [x1 - 200, y1], [x1 - 200, y1], [x1 + 300, y1]],
                     'top': top})
                # print('равенство', number)
    except:
        pass

    return obj


def line_add_to_successor(obj_successor: dict):
    w = obj_successor['w']
    try:
        h = obj_successor['h']
    except:
        h = 105
    x1 = 0
    y1 = h / 2
    x2 = -60
    y2 = 56

    obj_successor.update(
        {'line_coordinate': [[x1, y1], [x2, y2]]})
    return obj_successor
