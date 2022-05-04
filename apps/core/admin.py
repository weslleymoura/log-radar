from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import DataPoint

#admin.site.unregister(User)
#admin.site.unregister(Group)


admin.site.site_header = 'Log Radar Login'
admin.site.site_title = 'Log Radar Admin'

class DataPointAdmin(admin.ModelAdmin):
    list_display = ['origin', 'destination', 'dim_1', 'dim_2', 'is_active', 'is_train', 'business_key', 'date_created', 'date_modified']

admin.site.register(DataPoint, DataPointAdmin)