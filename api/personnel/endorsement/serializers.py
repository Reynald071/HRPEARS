from rest_framework import serializers

from backend.pas.endorsement.models import PasEndorsement, PasEndorsementPeople


class CapitalizedCharField(serializers.CharField):
    def to_representation(self, value):
        return value.upper()


class EndorsementSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format="%Y-%m-%d")
    people = serializers.CharField(source='get_all_people', read_only=True)
    created_by = serializers.CharField(source='preparedby.pi.user.get_fullname', read_only=True)

    class Meta:
        model = PasEndorsement
        fields = ['id', 'date', 'created_by', 'people']


class EndorsementPeopleSerializer(serializers.ModelSerializer):
    last_name = CapitalizedCharField(source='emp.pi.user.last_name', read_only=True)
    first_name = CapitalizedCharField(source='emp.pi.user.first_name', read_only=True)
    middle_name = CapitalizedCharField(source='emp.pi.user.middle_name', read_only=True)
    suffix = CapitalizedCharField(source='emp.pi.ext.name', read_only=True)
    position = CapitalizedCharField(source='position.name', read_only=True)
    empstatus = CapitalizedCharField(source='empstatus.name', read_only=True)
    fundcharge = CapitalizedCharField(source='fundcharge.name', read_only=True)
    effectivity_contract = serializers.DateField(format="%Y-%m-%d")
    end_of_contract = serializers.DateField(format="%Y-%m-%d")
    account_number = serializers.CharField(source='emp.account_number', read_only=True)

    class Meta:
        model = PasEndorsementPeople
        fields = ['id', 'last_name', 'first_name', 'middle_name', 'suffix', 'basic_salary', 'premium_rate',
                  'effectivity_contract', 'end_of_contract', 'empstatus', 'remarks', 'fundcharge', 'position',
                  'vice', 'account_number']