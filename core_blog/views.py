from uuid import UUID
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from .models import BlogPost
from .serializer import BlogSerializer

class BlogsView(APIView):
    """
    API view to fetch all blog posts in descending order of their posting date.
    Results are cached for optimized performance.
    """
    
    CACHE_KEY = 'blogs_list'
    CACHE_TIMEOUT = 300  # Cache timeout in seconds (e.g., 5 minutes)

    class BlogPagination(PageNumberPagination):
        """
        Custom pagination class for blog posts.
        """
        page_size = 10  # Number of items per page
        page_size_query_param = 'page_size'  # Allows client to customize the page size
        max_page_size = 100  # Maximum allowed page size

    def get(self, request):
        """
        Handles GET requests to retrieve a list of blog posts.
        """
        # Check if the cached data is available
        blogs_data = cache.get(self.CACHE_KEY)
        
        if not blogs_data:
            # Query database and serialize data
            blogs = BlogPost.objects.all().order_by('-date_posted')
            blogs_data = BlogSerializer(blogs, many=True).data
            
            # Store serialized data in cache
            cache.set(self.CACHE_KEY, blogs_data, timeout=self.CACHE_TIMEOUT)

        # Apply pagination
        paginator = self.BlogPagination()
        paginated_blogs = paginator.paginate_queryset(blogs_data, request)
        
        # Return paginated response
        return paginator.get_paginated_response(paginated_blogs)



class BlogDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, key):
        try:
            # Validate UUID
            UUID(key)
        except ValueError:
            return Response({"error": "Invalid UUID provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            blog_detail = BlogPost.objects.get(id=key)
        except BlogPost.DoesNotExist:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

        post_serialize = BlogSerializer(blog_detail).data
        return Response(post_serialize, status=status.HTTP_200_OK)