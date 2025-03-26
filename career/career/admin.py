from django.contrib import admin
from career.models import *
from django.forms import TextInput, Textarea
from django.db import models
class PersonsAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '200'})},
        # models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
    }
    list_display = ['person_name', 'position_full_name', 'department_short_name', 'person_id', 'img']
    search_fields = ['person_name', 'person_fio', 'person_id']
    save_as = True
    class Meta:
        model = Persons


admin.site.register(Persons, PersonsAdmin)
admin.site.register(SOrganization)
admin.site.register(SPosition)
admin.site.register(SDepartment)
admin.site.register(SPerson)