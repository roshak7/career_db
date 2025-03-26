from career.add_to_node import line_add_to_position


def generate_edges(org_list):
    ww = org_list[0]['w']
    # print(org_list[0]['ymax'])
    k=0
    if org_list[0]['ymax']<300:
        k=20
    xx2 = ((org_list[0]['x'] + ww)) / 10 - 10
    for count, org in enumerate(org_list):
        org_list[count] = line_add_to_position(org_list[count], count, len(org_list))
        # print(org_list[count])
        # org_list[count].update({'edges': [[random.randint(100, 200), 55], [random.randint(100, 200), 55]]})

        ww = org_list[count]['w']

        yy1 = (org_list[count]['y'] + ww / 2) / 10

        yy1 = org_list[count]['ymax']/10 - 4+k
        if len(org_list) > 13:
            if count > 8 and count <= 16:
                yy1 = yy1*0.96
            if count > 16:
                yy1 = yy1*0.94
        xx1 = (org_list[count]['x'] + ww / 2) / 10 + 10-0.2
        if count != 0:
            # print(xx1, xx2, yy1,count)
            org_list[count].update({'edges': [[xx2-0.2, yy1], [xx1, yy1]]})
    return org_list