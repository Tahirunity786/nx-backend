from django.contrib import admin
from .models import Chatmessage, ChatThread
# Register your models here.
admin.site.register(ChatThread)
admin.site.register(Chatmessage)