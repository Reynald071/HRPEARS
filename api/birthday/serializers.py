from rest_framework import serializers

from backend.models import Empprofile


class BirthdaySerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='pi.user.get_fullname', read_only=True)
    birth_day = serializers.IntegerField(source='pi.dob.day', read_only=True)

    class Meta:
        model = Empprofile
        fields = ['id_number', 'picture', 'full_name', 'birth_day']
