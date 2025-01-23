from rest_framework import serializers
from core_message.models import Chatmessage
from core_control.models import CustomUser




class UserSmallSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CustomUser
        fields = ('id','first_name', 'last_name')
    
   

class ChatMessageSerializer(serializers.ModelSerializer):
    user = UserSmallSerializer(many=False)
    class Meta:
        model = Chatmessage
        fields = '__all__'