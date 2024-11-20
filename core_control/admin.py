from django.contrib import admin
from core_control.models import Service, BlogPost, BlogPostImage, Comment, ContactUS

# Register your models here.
admin.site.register(Service)
admin.site.register(BlogPost)
admin.site.register(BlogPostImage)
admin.site.register(Comment)
admin.site.register(ContactUS)
