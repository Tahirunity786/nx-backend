import uuid
from rest_framework.views import Response, APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from core_control.serializer import UserSerializer, ContactSerializer, PorfolioSerializer, ServicesSerializer, AnonymousUserSerializer
from core_control.models import Portfolio, Service, AnonymousCookies, TokenSaver
from core_control.email import send_nx_email
from django.contrib.auth import get_user_model, authenticate
from core_control.utiles import get_tokens_for_user, generate_jwt_token, decode_jwt_token
from core_control.models import CustomUser
User = get_user_model()


class DashboardLogin(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data_login = UserSerializer(data=request.data)
        if data_login.is_valid():
            username = data_login.validated_data.pop('username', '')
            password = data_login.validated_data.pop('password', '')

            try:
                user = User.objects.get(username = username)
            except User.DoesNotExist:
                return Response({'error':"User not exist."}, status=status.HTTP_400_BAD_REQUEST)

            authenticated_user = authenticate(request, user.username, password)
            
            if authenticated_user is None:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            
            token = get_tokens_for_user(authenticated_user)

            return Response({'token':token}, status=status.HTTP_200_OK)
        
        return Response(data_login.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenViewSaver(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data_token = request.data.get('token')
        fcm_token = request.data.get('fcm_token')
        try:
            if not data_token and fcm_token:
                return Response({'success':False}, status=status.HTTP_400_BAD_REQUEST)
            
            user_id = decode_jwt_token(token=data_token)
            if not user_id:
                return Response({'success':False}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                cooke = AnonymousCookies.objects.get(cookie=user_id)
                user = cooke.user

            except CustomUser.DoesNotExist:
                return Response({'success':False}, status=status.HTTP_400_BAD_REQUEST)
            
            if user.fcm_token and user.fcm_token.token: return Response({'success':True}, status=status.HTTP_200_OK)
            
            fcm_token = TokenSaver.objects.create(token=fcm_token)
            
            user.fcm_token = fcm_token
            user.save()

            return Response({'success':True}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'success':False}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'success':False}, status=status.HTTP_400_BAD_REQUEST)
        
        
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
    

class CookiesHandler(APIView):
 
    def post(self, request):
        """
        Handles cookie creation and returns the saved cookie to the client.
        """
        # Serialize and validate the incoming data
        data = AnonymousUserSerializer(data=request.data)
   
        
        if data.is_valid():
            # Save the validated data to the database
            cookie_instance = data.save()
            raw_cookie = cookie_instance.cookie
            cookie = generate_jwt_token(raw_cookie)

            # Prepare the response and set the cookie
            response = Response(
                {
                    "success":True,
                    "cookie": cookie,
                },
                status=status.HTTP_201_CREATED,
            )
            return response

        # If data is invalid, return errors
        return Response(
            {"error": "Invalid data", "details": data.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
