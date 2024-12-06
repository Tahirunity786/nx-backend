from django.urls import path
from core_blog.views import BlogsView, BlogDetailView
urlpatterns = [
    path('all-blogs', BlogsView.as_view()),
    path('sp-blog/<str:key>/', BlogDetailView.as_view())
]
