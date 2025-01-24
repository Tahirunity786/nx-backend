from django.urls import path
from core_control.views import ContactView, PortfolioView, ServicesSpreaderView, CookiesHandler, DashboardLogin, TokenViewSaver
urlpatterns = [
    path('all-services', ServicesSpreaderView.as_view(), name="services-all"),
    path('contact-us', ContactView.as_view(), name="contact"),
    path('all-porfolio', PortfolioView.as_view(), name="contact"),


    # Cookie
    path('secure', CookiesHandler.as_view(), name="secure"),
    path('fcm_notify_saver', TokenViewSaver.as_view(), name="fcm_notify_saver"),

    # Auth api
    path('login', DashboardLogin.as_view(), name="login"),





]
