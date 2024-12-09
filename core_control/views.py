from rest_framework.views import Response, APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from core_control.serializer import ContactSerializer, PorfolioSerializer, ServicesSerializer
from core_control.models import Portfolio, Service
from core_control.email import send_nx_email


class ServicesSpreaderView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if not Service.objects.exists():
            return Response({'error': "No services found."}, status=status.HTTP_404_NOT_FOUND)

        services = Service.objects.all()
        serializer = ServicesSerializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ContactView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Validate the incoming data
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            # Save the data and access serialized data
            serializer.save()
            # Access saved instance data directly
            serialize_data = serializer.data

            # Log email for debugging
            email = serialize_data.get("email")
            name = serialize_data.get("name")

            # Send email asynchronously for scalability
            if email:
                send_nx_email(email, name)
            # Return success response
            response = {"success": "Your message has been received successfully."}
            return Response(response, status=status.HTTP_200_OK)
        # Handle validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PortfolioView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        portfolio_data = Portfolio.objects.all().order_by('-id')
        sanitized_data = PorfolioSerializer(portfolio_data, many=True).data
        return Response(sanitized_data, status=status.HTTP_200_OK)
    

