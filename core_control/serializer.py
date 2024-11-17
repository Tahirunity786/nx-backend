from rest_framework import serializers
from core_control.models import ContactUS, Service

class ServicesSerializer(serializers.ModelSerializer):
    _id = serializers.CharField(read_only=True)
    services_slug = serializers.CharField(read_only=True)
    
    class Meta:
        model = Service
        fields = ('_id', 'services_slug', 'image_pb_id','title', 'description')

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUS
        fields = ('name', 'subject', 'email', 'message_detail')