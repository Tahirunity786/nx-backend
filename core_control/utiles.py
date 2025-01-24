from rest_framework_simplejwt.tokens import RefreshToken
import jwt
import datetime
from django.conf import settings


def get_tokens_for_user(user):
    """
    Generate refresh and access tokens for a given user.

    This function generates a refresh token and an access token for the provided user.
    The access token is used for authenticating the user for subsequent requests,
    while the refresh token is used to obtain a new access token once it expires.

    Args:
        user (User): The user for whom tokens are generated.

    Returns:
        dict: A dictionary containing the refresh token and access token.

    Example:
        user = User.objects.get(username='example')
        tokens = get_tokens_for_user(user)
        # Output: {'refresh': '...', 'access': '...'}
    """
    # Generate a refresh token for the user
    refresh = RefreshToken.for_user(user)

    # Return tokens as strings for easier serialization
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def generate_jwt_token(ID):
        # Convert UUID to a string before adding it to the payload
        payload = {
            'user_id': str(ID),  # Convert UUID to string
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=120)  # Token expires in 4 months
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return token


def decode_jwt_token(token):

    try:
        #   Convert token
        # Decode JWT and validate user
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    
        user_id = payload.get('user_id')
        if not user_id:
            print("Invalid token payload: user_id missing")
            raise None
        
        return user_id
        
    except jwt.ExpiredSignatureError:
         print("Token expired")
         raise None
        
    except jwt.InvalidTokenError:
         print("Invalid token")
         raise None
    

