from django.urls import path
from core_blog.views import BlogsView
urlpatterns = [
    path('all-blogs', BlogsView.as_view())
]
