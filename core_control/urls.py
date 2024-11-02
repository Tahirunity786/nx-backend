from django.urls import path
from core_control.views import ServicesSpreaderView
urlpatterns = [
    path('all-services', ServicesSpreaderView.as_view(), name="services-all")
]
