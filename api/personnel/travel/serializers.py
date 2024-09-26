from rest_framework import serializers

from frontend.models import Ritopeople, Ritodetails, Rito


class TravelHistorySerializers(serializers.ModelSerializer):
    tracking_no = serializers.CharField(source='detail.rito.tracking_no', read_only=True)
    tracking_merge = serializers.CharField(source='detail.rito.tracking_merge', read_only=True)
    place = serializers.CharField(source='detail.place', read_only=True)
    inclusive_from = serializers.CharField(source='detail.inclusive_from', read_only=True)
    inclusive_to = serializers.CharField(source='detail.inclusive_to', read_only=True)
    purpose = serializers.CharField(source='detail.purpose', read_only=True)
    expected_output = serializers.CharField(source='detail.expected_output', read_only=True)
    mot = serializers.CharField(source='detail.mot.name', read_only=True)
    claims = serializers.CharField(source='detail.claims.name', read_only=True)
    attachment = serializers.CharField(source='detail.rito.get_attachment', read_only=True)

    class Meta:
        model = Ritopeople
        fields = ['id', 'tracking_no', 'tracking_merge', 'place', 'inclusive_from', 'inclusive_to', 'purpose', 'expected_output',
                  'mot', 'claims', 'attachment']


class TravelDetailsSerializers(serializers.ModelSerializer):
    claims = serializers.CharField(source='claims.name', read_only=True)
    passengers = serializers.CharField(source='get_tr_passengers', read_only=True)
    mot = serializers.CharField(source='mot.name', read_only=True)

    class Meta:
        model = Ritodetails
        fields = ['id', 'passengers', 'place', 'purpose', 'inclusive_from', 'inclusive_to', 'expected_output', 'claims',
                  'mot']


class TravelSerializers(serializers.ModelSerializer):
    hash = serializers.CharField(source='get_hash', read_only=True)
    requesting_office = serializers.CharField(source='emp.pi.user.get_fullname', read_only=True)
    rito_approver = serializers.CharField(source='get_rito_approver', read_only=True)

    passengers = serializers.CharField(source='get_all_passengers', read_only=True)
    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S %p", read_only=True)
    travel_status = serializers.CharField(source='get_travel_status', read_only=True)
    travel_status_for_supervisor = serializers.CharField(source='get_travel_status_for_supervisor', read_only=True)
    action = serializers.CharField(source='get_action', read_only=True)
    admin_action = serializers.CharField(source='get_admin_action', read_only=True)
    supervisor_action = serializers.CharField(source='get_supervisor_action', read_only=True)
    travel_confirmation = serializers.CharField(source='count_confirmation_travel', read_only=True)
    travel_justification = serializers.CharField(source='count_justification_travel', read_only=True)

    class Meta:
        model = Rito
        fields = ['id', 'hash', 'tracking_no', 'tracking_merge', 'passengers', 'date', 'status', 'travel_status',
                  'travel_status_for_supervisor', 'action', 'admin_action', 'supervisor_action', 'travel_confirmation',
                  'travel_justification', 'requesting_office', 'rito_approver']
