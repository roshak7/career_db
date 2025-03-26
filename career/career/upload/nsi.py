from career.models import *
import hashlib


def uid_generate(s=''):
    m = hashlib.md5()
    m.update(s.lower().encode("utf8"))
    return m.hexdigest()[0:20]

def update_si_organization():
    persons = Persons.objects.all()
    for p in persons:
        # if p.organization_id == None:
        if '=IF' in p.organization_name:
            pass
        else:
            org_name = p.organization_name
            org_uid = uid_generate(s=str(org_name))
            org, created = SOrganization.objects.update_or_create(
                uid=org_uid, defaults={"name": org_name, 'jdata':{'value':org_name}}
            )

            p.organization_id = org_uid
            p.position_id = update_si_position(org, p.position_full_name, p.position_short_name)
            p.department_id = update_si_department(org, p.department_full_name, p.department_short_name)
        p.save()

    return 'OK'

def update_si_position(org, name, shortname):
    uid = uid_generate(s=str(name))
    pos, created = SPosition.objects.update_or_create(
        id_sorganization=org, uid=uid, defaults={"name": name, 'jdata':{'idorg':org.id, 'value':name, 'shortValue':shortname}})
    return pos.uid

def update_si_department(org, name, shortname):
    if name != None and name != '':
        uid = uid_generate(s=str(name))
        dep, created = SDepartment.objects.update_or_create(
            id_sorganization=org, uid=uid, defaults={"name": name, 'jdata':{'value':name, 'shortValue':shortname}})
        return dep.uid
    return None

def update_si_organization_1(uidperson):
    p = Persons.objects.get(person_id=uidperson)
    try:
        o = SOrganization.objects.get(uid=p.organization_id)
        return [o.uid, o.id]
    except:

    # if p.organization_id == None:
        if '=IF' in p.organization_name:
            pass
        else:
            org_name = p.organization_name
            org_uid = uid_generate(s=str(org_name))
            org, created = SOrganization.objects.update_or_create(
                uid=org_uid, defaults={"name": org_name, 'jdata':{'value':org_name}}
            )

            p.organization_id = org_uid
            p.position_id = update_si_position(org, p.position_full_name, p.position_short_name)
            p.department_id = update_si_department(org, p.department_full_name, p.department_short_name)
        p.save()

        return p.organization_id