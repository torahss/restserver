from django.contrib import admin
from quickstart.models import SensorData

class SensorDataAdmin(admin.ModelAdmin) :
    list_display = ('station', 'tpm', 'temp')


admin.site.register(SensorData,SensorDataAdmin)



# Register your models here.
