from rest_framework import serializers

from frontend.lds.models import LdsRso, LdsParticipants, LdsFacilitator, LdsIDP


class LdsRsoSerializer(serializers.ModelSerializer):
    training_title = serializers.CharField(source='training.tt_name', read_only=True)
    inclusive_dates = serializers.CharField(source='get_inclusive_dates', read_only=True)
    date_added = serializers.DateTimeField(format="%b %d, %Y %H:%M:%S %p", read_only=True)
    status = serializers.CharField(source='get_status', read_only=True)
    created_by = serializers.CharField(source='created_by.pi.user.get_fullname', read_only=True)

    class Meta:
        model = LdsRso
        fields = ['id', 'training_title', 'inclusive_dates', 'date_added', 'status', 'venue', 'created_by']


class LdsParticipantsSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='emp.pi.user.get_fullname', read_only=True)
    position = serializers.CharField(source='emp.position.name', read_only=True)
    type = serializers.CharField(source='get_participant_type', read_only=True)

    class Meta:
        model = LdsParticipants
        fields = ['id', 'rso_id', 'full_name', 'type', 'position', 'participants_name']


class LdsFacilitatorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='emp.pi.user.get_fullname', read_only=True)
    position = serializers.CharField(source='emp.position.name', read_only=True)

    class Meta:
        model = LdsFacilitator
        fields = ['id', 'rso_id', 'full_name', 'is_resource_person', 'position', 'emp_id', 'rp_name', 'is_group']


class LdsIDPSerializer(serializers.ModelSerializer):
    date_created = serializers.DateTimeField(format="%b %d, %Y %H:%M:%S %p", read_only=True)
    date_updated = serializers.DateTimeField(format="%b %d, %Y %H:%M:%S %p", read_only=True)

    class Meta:
        model = LdsIDP
        fields = '__all__'
