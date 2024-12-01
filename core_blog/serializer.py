from rest_framework import serializers
from core_blog.models import BlogPostImageO, BlogPost

class BlogImagesSrealizer(serializers.ModelSerializer):
    class Meta:
        model = BlogPostImageO
        fields = ['image_pb_id']


class BlogSerializer(serializers.ModelSerializer):
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = ['id', 'post_slug', 'cover_image', 'title','content', 'tag', 'date_posted']

    def get_cover_image(self, obj):
        # Check if images are available, and return the first image
        if obj.images.exists():
            first_image = obj.images.first()
            return BlogImagesSrealizer(first_image).data
        return None  # Return None if no images are available
