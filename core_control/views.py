from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers

from rest_framework.views import Response, APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from core_control.serializer import ServicesSerializer
from core_control.models import Service



# @method_decorator(cache_page(60 * 60 * 2), name='dispatch')
# @method_decorator(vary_on_cookie, name='dispatch')
class ServicesSpreaderView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if not Service.objects.exists():
            return Response({'error': "No services found."}, status=status.HTTP_404_NOT_FOUND)

        services = Service.objects.all()
        serializer = ServicesSerializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)