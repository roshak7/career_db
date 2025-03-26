import hashlib


def id_generate(s='', pos='вакансия'):
    m = hashlib.md5()
    if "вакансия" in s.lower():
        m.update(pos.lower().encode("utf8"))
    else:
        m.update(s.lower().encode("utf8"))

    return m.hexdigest()[0:20]