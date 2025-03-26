from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.conf import settings
import hashlib

class CareerAbstract(models.Model):
    uid = models.CharField(max_length=100, verbose_name='UID')
    name = models.CharField(max_length=1000, verbose_name='Имя')
    jdata = JSONField(verbose_name='JSON данные', null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        abstract = True

    def __str__(self):
        return "%s" % (self.name)





class SOrganization(CareerAbstract):
    class Meta:
        verbose_name = 'Справочник Организация'
        verbose_name_plural = 'Справочник Организаций'

    def save(self, *args, **kwargs):
        self.name = self.jdata['value']
        m = hashlib.md5()
        m.update(self.name.lower().encode("utf8"))
        self.uid = m.hexdigest()[0:20]
        self.jdata['uid'] = self.uid

        super().save(*args, **kwargs)


class SDepartment(CareerAbstract):
    id_sorganization = models.ForeignKey(SOrganization, blank=True, null=True, on_delete=models.CASCADE)
    class Meta:
        verbose_name = 'Справочник Подоазделение'
        verbose_name_plural = 'Справочник Подразделений'
    def save(self, *args, **kwargs):
        self.name = self.jdata['value']
        try:
            self.id_sorganization_id = int(self.jdata['idorg'])
        except:
            self.id_sorganization = None
        m = hashlib.md5()
        m.update(self.name.lower().encode("utf8"))
        self.uid = m.hexdigest()[0:20]
        self.jdata['uid'] = self.uid

        super().save(*args, **kwargs)

class SPosition(CareerAbstract):
    id_sorganization = models.ForeignKey(SOrganization, blank=True, null=True, on_delete=models.CASCADE)
    id_sdepartment = models.ForeignKey(SDepartment, blank=True, null=True, on_delete=models.CASCADE)
    class Meta:
        verbose_name = 'Справочник Должность'
        verbose_name_plural = 'Справочник Должностей'

    def save(self, *args, **kwargs):
        self.name = self.jdata['value']
        self.id_sorganization_id = int(self.jdata['idorg'])
        try:
            self.id_sdepartment_id = int(self.jdata['iddep'])
        except:
            pass
        m = hashlib.md5()
        m.update(self.name.lower().encode("utf8"))
        self.uid = m.hexdigest()[0:20]
        self.jdata['uid'] = self.uid

        super().save(*args, **kwargs)
class SPerson(CareerAbstract):
    id_sorganization = models.ForeignKey(SOrganization, blank=True, null=True, on_delete=models.CASCADE)
    id_sposition = models.ForeignKey(SPosition, blank=True, null=True, on_delete=models.CASCADE)
    id_sdepartment = models.ForeignKey(SDepartment, blank=True, null=True, on_delete=models.CASCADE)
    class Meta:
        verbose_name = 'Справочник Сотрудник'
        verbose_name_plural = 'Справочник Сотрудников'

    def save(self, *args, **kwargs):
        self.name = self.jdata['person_fio']
        try:
            self.id_sorganization_id = int(self.jdata['idorg'])
        except:
            pass
        try:
            self.id_sdepartment_id = int(self.jdata['iddep'])
        except:
            pass
        try:
            self.id_sposition_id = int(self.jdata['idpos'])
        except:
            pass
        m = hashlib.md5()
        m.update(self.name.lower().encode("utf8"))
        self.uid = m.hexdigest()[0:20]
        self.jdata['uid'] = self.uid
        self.jdata['value'] = self.jdata['person_fio']
        self.jdata['shortValue'] = self.jdata['person_name']
        self.jdata['idpers'] = self.id

        super().save(*args, **kwargs)
class TreeFolders(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Наименование папки')
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Дерево папок'
        verbose_name_plural = 'Дерево папок'
    def __str__(self):
        if self.parent:
            return "%s (%s)" % (self.name, self.parent.name)
        else:
            return "%s" % (self.name)

class Career_structure(models.Model):
    id_card_successor = models.CharField(max_length=300, null=True, blank=True, verbose_name='ID карты преемников')
    name =models.CharField(max_length=300, null=True, blank=True, verbose_name='Наименование карты преемников')
    company = models.CharField(max_length=300, null=True, blank=True, verbose_name='Наименование предприятия')
    type_map = models.CharField(max_length=30, null=True, blank=True, verbose_name='Тип карты')  # type_map:   [singlelevel, multilevel]
    jdata_org_structure = JSONField(verbose_name='JSON данные структуры', null=True, blank=True)
    jdata_org_successor = JSONField(verbose_name='JSON данные по преемникам', null=True, blank=True)
    jdata_card_changes = JSONField(verbose_name='JSON данные сохранение изменений', null=True, blank=True)
    jdata_card_draft = JSONField(verbose_name='JSON данные черновика', null=True, blank=True)
    jdata_card_default = JSONField(verbose_name='JSON данные по умолчани сохраненные из конструктора', null=True, blank=True)
    draft = models.BooleanField(verbose_name='Черновик (да/нет)', default=False)
    jdata_persons = JSONField(verbose_name='JSON данные о сотрудниках', null=True, blank=True)
    jdata_persons_photos = JSONField(verbose_name='JSON фото сотрудников', null=True, blank=True)
    id_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Автор')
    id_folder = models.BigIntegerField(default=0, verbose_name='id папки', null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Карта c преемниками'
        verbose_name_plural = 'Карты с преемниками'

    # @property
    # def persons_list(self):
    #     persons = Persons.objects.all()
    #     persons_serializer = PersonSerializer(persons)
    #     return persons_serializer
    def __str__(self):
        return "%s" % (self.name)


class Career_data(models.Model):
    name = models.CharField(max_length=300, null=True, blank=True, verbose_name='Наименование структуры')
    jdata = JSONField(verbose_name='JSON данные', null=True, blank=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Оргструктура с преемниками'
        verbose_name_plural = 'Оргструктуры с преемниками'

    def __str__(self):
        return "%s" % (self.name)


class Person_photo(models.Model):
    name = models.CharField(max_length=300, null=True, blank=True, verbose_name='Имя сотрудника')
    idperson = models.CharField(unique=True, max_length=100, null=True, blank=True, verbose_name='ID сотрудника')
    idphoto = models.CharField(unique=True, max_length=100, null=True, blank=True, verbose_name='ID фотографии')
    img = models.ImageField(null=True, blank=True, verbose_name='Фото сотрудника', upload_to='img')

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Фото сотрудника'
        verbose_name_plural = 'Фото сотрудников'

    def __str__(self):
        return "%s" % (self.name)



class Person_profile(models.Model):
    name = models.CharField(max_length=300, null=True, blank=True, verbose_name='Имя файла')
    idperson = models.CharField(unique=True, max_length=100, null=True, blank=True, verbose_name='ID сотрудника')
    profile_file = models.FileField(null=True, blank=True, verbose_name='Файл профиля сотрудника', upload_to='profile', default='')
    jdata = JSONField(verbose_name='JSON данные', null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Файл профиля сотрудника'
        verbose_name_plural = 'Файлы профилей сотрудников'

    def __str__(self):
        return "%s" % (self.name)
class Persons(models.Model):
    organization_name = models.CharField(max_length=300, null=True, blank=True, verbose_name='Наименование предприятия',
                                         help_text='тип string, содержит наименование предприятия')
    organization_id = models.CharField(max_length=100, null=True, blank=True, verbose_name='ID предприятия',
                                       help_text='тип string, содержит код предприятия')  # тип string, содержит код предприятия,
    department_id = models.CharField(max_length=100, null=True, blank=True, verbose_name='ID подразделения',
                                     help_text='тип string, состоит из [код предприятия]+[код подразделения]')  # тип string, состоит из [код предприятия]+[код подразделения],
    department_short_name = models.CharField(max_length=100, null=True, blank=True,
                                             verbose_name='Краткое название подразделения')  # тип string - краткое название подразделения. Выводится на экран в ноде. При первоначальной загрузке из БД устанавливается равным departmentFullName,
    department_full_name = models.CharField(max_length=300, null=True, blank=True,
                                            verbose_name='Полное название подразделения')  # тип string - полное название подразделения. Выводится во всплывающей подсказке. Равно названию подразделения в кадровой системе
    person_id = models.CharField(max_length=100, null=True, blank=True, verbose_name='ID сотрудника',
                                 help_text='тип string, состоит из [код предприятия]+[табельный номер]. Для лиц не являющихся работниками предприятия вместо табельного должен генерироваться другой код')  # тип string, состоит из [код предприятия]+[табельный номер]. Для лиц не являющихся работниками предприятия вместо табельного должен генерироваться другой код,
    person_id_photo = models.CharField(max_length=100, null=True, blank=True,
                                       verbose_name='ID сотрудника для хранения фото',
                                       help_text='тип string, MD5 из ФИО в маленьком рогистре.')
    person_tab_num = models.CharField(max_length=100, null=True, blank=True,
                                      verbose_name='Табельный номер сотрудника')  # тип string, Табельный номер. Для лиц не являющихся работниками предприятия вместо табельного должен генерироваться другой код,
    person_name = models.CharField(max_length=100, null=True, blank=True,
                                   verbose_name='Сокращенное имя сотрудника')  # тип string, Выводится на экран в ноде. По умолчанию - Фамилия И.О.,
    person_fio = models.CharField(max_length=100, null=True, blank=True,
                                  verbose_name='Полное имя сотрудника')  # тип string - полное ФИО. Выводится во всплывающей подсказке. Равно ФИО в кадровой системе,
    position_critical = models.CharField(max_length=100, null=True, blank=True,
                                         verbose_name='Критически важная должность')  # тип string - Критически важная должность,
    protection = models.CharField(max_length=100, null=True, blank=True,
                                  verbose_name='Защищенность')  # тип string - Защищенность
    position_id = models.CharField(max_length=100, null=True, blank=True, verbose_name='ID должности',
                                     help_text='тип string')  # тип string, состоит из [код предприятия]+[код должности],
    position_short_name = models.CharField(max_length=300, null=True, blank=True,
                                           verbose_name='Краткое название должности')  # тип string - Краткое название должности. Выводится на экран в ноде для преемника. Если для работника есть нода - должно соответствовать positionShortName.,
    position_full_name = models.CharField(max_length=1000, null=True, blank=True,
                                          verbose_name='Полное название должности')  # тип string - полное название должности. Выводится во всплывающей подсказке. Равно названию должности в кадровой системе
    birthday = models.DateField(null=True, blank=True,
                                verbose_name='Дата рождения работника')  # тип Date. Дата рождения работника. Равно дате рождения в кадровой системе,
    scientific_degree = models.CharField(max_length=500, null=True, blank=True,
                                         verbose_name='Ученая степень')  # тип string - ученая степень. Выводится на экран в ноде.,
    personnel_reserve = models.CharField(max_length=300, null=True, blank=True,
                                         verbose_name='Управленческий кадровый резерв (УКР)')  # тип string - управленческий кадровый резерв. Выводится на экран в ноде.,
    personnel_reserve_dop = models.CharField(max_length=300, null=True, blank=True,
                                             verbose_name='Управленческий кадровый резерв (УКР доп)')  # тип string - управленческий кадровый резерв. Выводится на экран в ноде.,
    contract_end_date = models.DateField(null=True, blank=True,
                                         verbose_name='Дата завершения трудового договора')  # тип string - дата завершения трудового договора,
    assessment_potential = models.CharField(max_length=100, null=True, blank=True,
                                            verbose_name='Оценка потенциала')  # тип string - оценка потенциала,
    assessment_potential_year = models.CharField(max_length=10, null=True, blank=True,
                                            verbose_name='Год Оценки потенциала')  # тип string - оценка потенциала,
    readiness = models.CharField(max_length=100, null=True, blank=True,
                                 verbose_name='Оценка готовности')  # тип string - оценка готовности,
    mobility = models.CharField(max_length=100, null=True, blank=True,
                                verbose_name='Мобильность сотрудника')  # тип string - мобильность сотрудника,
    kpi_3 = models.FloatField(null=True, blank=True,
                              verbose_name='КПЭ поза-позапрошлого года')  # float. КПЭ поза-позапрошлого года,
    kpi_2 = models.FloatField(null=True, blank=True,
                              verbose_name='КПЭ позапрошлого года')  # float. КПЭ позапрошлого года,
    kpi_1 = models.FloatField(null=True, blank=True, verbose_name='КПЭ прошлого года')  # float. КПЭ прошлого года,
    profile = models.BooleanField(default=False,
                                  verbose_name='Наличие профиля преемника')  # boolean. Наличие профиля преемника,
    profile_id = models.CharField(max_length=100, null=True, blank=True,
                                  verbose_name='ID профиля преемника')  # string. ID профиля преемника - пока на вырост,
    participation_assessment = models.BooleanField(default=False,
                                                   verbose_name=' Участвовал в оценочных мероприятиях')  # boolean. Участвовал в оценочных мероприятиях,
    age = models.CharField(max_length=3, null=True, blank=True,
                           verbose_name='Возраст')  # string. Возраст
    img = models.ImageField(null=True, blank=True, verbose_name='Фото сотрудника', upload_to='img', default='')


    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cотрудник'
        verbose_name_plural = 'Cотрудники'

    def __str__(self):
        return "%s (%s)" % (self.person_fio, self.position_short_name)


class Organization(models.Model):
    organization_id = models.CharField(max_length=100, null=True, blank=True,
                                       verbose_name='ID предприятия')  # тип string, содержит код предприятия,
    organization_name = models.CharField(max_length=500, null=True, blank=True,
                                         verbose_name='Полное наименование предприятия')  # тип string, полное наименование предприятия,
    organization_short_name = models.CharField(max_length=100, null=True, blank=True,
                                               verbose_name='Краткое наименование предприятия')  # тип string, Краткое наименование предприятия,
    organization_idmd5 = models.CharField(max_length=100, null=True, blank=True,
                                       verbose_name='ID md5 предприятия')  # тип string, содержит ID предприятия в MD5 ,

    class Meta:
        verbose_name = 'Предприятие'
        verbose_name_plural = 'Предприятия'

    def __str__(self):
        return "%s" % (self.organization_short_name)


class Position(models.Model):
    position_id = models.CharField(max_length=100, null=True, blank=True,
                                   verbose_name='ID должности')  # тип string, содержит код должности MD5
    position_name = models.CharField(max_length=500, null=True, blank=True,
                                     verbose_name='Полное наименование должности')  # тип string, полное наименование должности
    position_short_name = models.CharField(max_length=200, null=True, blank=True,
                                           verbose_name='Краткое наименование должности')  # тип string, Краткое наименование должности
    organization_id = models.CharField(max_length=100, null=True, blank=True,
                                       verbose_name='ID предприятия')  # тип string, содержит код предприятия

    protect = models.CharField(max_length=100, null=True, blank=True,
                                       verbose_name='Защищенность')  # тип string, защищенность

admin.site.register(Career_data)
admin.site.register(Person_photo)
admin.site.register(Career_structure)
admin.site.register(Organization)
admin.site.register(Person_profile)
admin.site.register(Position)
admin.site.register(TreeFolders)
