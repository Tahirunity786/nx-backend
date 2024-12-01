from django.contrib import admin
from core_control.models import Service, ContactUS, Technologies

# Register your models here.
admin.site.register(Service)

admin.site.register(ContactUS)
admin.site.register(Technologies)
