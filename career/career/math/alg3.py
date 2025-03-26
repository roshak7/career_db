from career.math.alg1 import *


def edges_correct(jdata, org_list):
    try:
        x = jdata[1]['x']
    except:
        x = 1000
    # fullsize = jdata[1]['full_size']
    count_str1 = 0
    count_str2 = 0
    coordinate_line = []
    x_in_line = []
    x_boss = jdata[0]['boss'][0][0]
    for i in range(1, len(jdata)):
        if jdata[i]['x'] == x:
            count_str1 += 1
    for i in range(1, len(jdata)):
        # print(jdata[i])
        # вычисляем кол-во рядов
        y1 = jdata[i]['y1'] / 10 + 4.5
        if jdata[i]['x'] == x:

            count_str2 += 1

            fullsize = jdata[i]['full_size'][0]
            if fullsize < 500:
                fullsize += OTSTUP_H / 2 - 10

            x = jdata[i]['x']
            x_in_line.append((x + fullsize) / 10 + 5.85)

            # coordinate_line = [[x_boss / 10 + 24.85, y1]]
            try:
                if count_str2 == count_str1:
                    coordinate_line += [[x_in_line[count_str2 - 2], y1]]
                else:
                    coordinate_line += [[x_in_line[count_str2-2], y1]] + [[x_in_line[count_str2 - 1], y1]]
            except:
                coordinate_line += [[x_in_line[count_str2 - 1], y1]]

        # print(jdata[i])
        org_list[i].update({'edges': coordinate_line + [[jdata[i]['boss'][0][0] / 10 + 24.86, y1]]})
        # print(coordinate_line)
    # for j in jdata:
    #     print(j)
    return org_list
