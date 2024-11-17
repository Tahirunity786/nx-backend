from django.urls import path
from core_control.views import ContactView, ServicesSpreaderView
urlpatterns = [
    path('all-services', ServicesSpreaderView.as_view(), name="services-all"),
    path('contact-us', ContactView.as_view(), name="contact")
]
