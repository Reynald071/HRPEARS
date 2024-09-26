from django.db.models.functions import Upper
from django_mysql.models.functions import SHA1
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from api.hrws.serializers import item_db_serialize, vest_db_serialize, intervention_db_serialize,covid_assistance_serialize,sweap_db_serialize, \
    emp_assistance_serialize, health_profile_serialize, sweap_gratuity_serialize, incident_report_serialize, sweap_membership_serialize
from backend.models import Empprofile
from backend.welfare_intervention.intervention.models import CovidAssistance, vest_db, activity_db, item_db, intervention, sweap_assistance, \
    sweap_gratuity, employee_assistance_sop, health_profile, sweap_gratuity, incidentreport_db, Sweap_membership
from api.personnel.employees.serializers import EmployeeAdminSerializer
from datetime import date
today = date.today()
month = today.strftime("%m")
year = today.strftime("%Y")

class EmployeeInterventionDatabaseViews(generics.ListAPIView):
    serializer_class = EmployeeAdminSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Empprofile.objects.filter(pi__user__is_active=True).all().order_by('pi__user__last_name')
        return queryset

class sweap_membership_view(generics.ListAPIView):
    queryset = Sweap_membership.objects.all().order_by('-dateadded')
    serializer_class = sweap_membership_serialize
    permission_classes = [IsAuthenticated]

class item_views(generics.ListAPIView):
    queryset = item_db.objects.filter(Q(activity_id=2)).order_by('-id')
    serializer_class = item_db_serialize
    permission_classes = [IsAuthenticated]


class vest_view(generics.ListAPIView):
    queryset = vest_db.objects.all()
    serializer_class = vest_db_serialize
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if self.request.query_params.get('status'):
            queryset = vest_db.objects.all().filter(status = self.request.query_params.get("status"))
            return queryset
        else:
            queryset = vest_db.objects.all().filter().order_by('-id')
            return queryset

 
class intervention(generics.ListAPIView):
    month = today.strftime("%m")
    year = today.strftime("%Y")
    queryset = intervention.objects.all().filter(date__year=year).order_by('-id')
    serializer_class = intervention_db_serialize
    permission_classes = [IsAuthenticated]


class covid_view(generics.ListAPIView):
    queryset = CovidAssistance.objects.all()
    serializer_class = covid_assistance_serialize
    permission_classes = [IsAuthenticated]


class sweap_view(generics.ListAPIView):
    serializer_class = sweap_db_serialize
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if self.request.query_params.get('status'):
            queryset = sweap_assistance.objects.all().filter(typeofassistant = self.request.query_params.get("status")).order_by('-id')
            return queryset
        else:
            queryset = sweap_assistance.objects.all().filter().order_by('-id')
            return queryset


class emp_assistance_view(generics.ListAPIView):
    serializer_class = emp_assistance_serialize
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if self.request.query_params.get('sex'):
            queryset = employee_assistance_sop.objects.all().filter(emp_id__pi_id__gender = self.request.query_params.get("sex")).order_by('-id')
            return queryset
        else:
            queryset = employee_assistance_sop.objects.all().filter().order_by('-id')
            return queryset

class health_profile_view(generics.ListAPIView):
    serializer_class = health_profile_serialize
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if self.request.query_params.get('status'):
            queryset = health_profile.objects.all().filter(category = self.request.query_params.get("status")).order_by('-id')
            return queryset
        else:
            queryset = health_profile.objects.all().filter().order_by('-id')
            return queryset

class sweap_gratuity_view(generics.ListAPIView):
    serializer_class = sweap_gratuity_serialize
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if self.request.query_params.get('status'):
            queryset = sweap_gratuity.objects.all().filter(type_of_assistance = self.request.query_params.get("status"))
            return queryset
        else:
            queryset = sweap_gratuity.objects.all()
            return queryset

class incident_report_view(generics.ListAPIView):
    serializer_class = incident_report_serialize
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.query_params.get('status'):
            queryset = incidentreport_db.objects.all().filter(category = self.request.query_params.get("status")).order_by('-id')
            return queryset
        else:
            queryset = incidentreport_db.objects.all().filter().order_by('-id')
            return queryset