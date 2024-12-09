from rest_framework import serializers
from core_control.models import ContactUS, Portfolio, PortfolioImages, Service

class ServicesSerializer(serializers.ModelSerializer):
    _id = serializers.CharField(read_only=True)
    services_slug = serializers.CharField(read_only=True)
    
    class Meta:
        model = Service
        fields = ('_id', 'services_slug', 'image_pb_id','title', 'description')


class ContactSerializer(serializers.ModelSerializer):
    # Add a field for the file assignment, ensuring it's handled properly
    file_assignment = serializers.FileField(
        required=False,
        allow_null=True,
        help_text="Optional file attachment for the contact form"
    )

    class Meta:
        model = ContactUS
        fields = ['name', 'subject', 'email', 'contact_no', 'message_detail', 'file_assignment']
        extra_kwargs = {
            'name': {'required': True, 'help_text': 'Full name of the contact'},
            'subject': {'required': False, 'help_text': 'Subject of the inquiry'},
            'email': {'required': True, 'help_text': 'Contact email address'},
            'contact_no': {'required': False, 'help_text': 'Optional contact number'},
            'message_detail': {'required': True, 'help_text': 'Details of the message'},
        }


class PortfolioImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioImages
        fields = ('media', 'tag')

class PorfolioSerializer(serializers.ModelSerializer):
    image = PortfolioImagesSerializer(many=True)
    class Meta:
        model = Portfolio
        fields = ('image', 'description')