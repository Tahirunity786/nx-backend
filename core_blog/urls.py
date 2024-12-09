from django.urls import path
from core_blog.views import BlogsView, BlogDetailView, LimitedBlogView, PostCommentView
urlpatterns = [
    path('all-blogs', BlogsView.as_view()),
    path('lm-blogs', LimitedBlogView.as_view()),
    path('sp-blog/<str:key>/', BlogDetailView.as_view()),
    path('post-on-comment/<str:key>/', PostCommentView.as_view()),
    path('show-post-comment/<str:key>/', PostCommentView.as_view()),
]
