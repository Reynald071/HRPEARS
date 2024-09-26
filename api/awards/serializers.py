from rest_framework import serializers

from backend.awards.models import AwGuidelines


class AwGuidelinesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AwGuidelines
        fields = '__all__'