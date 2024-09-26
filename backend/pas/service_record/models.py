from django.db import models
from django.utils import timezone

from backend.models import Empprofile
from frontend.models import Workhistory


class PasServiceRecord(models.Model):
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    drn = models.CharField(max_length=255, blank=True, null=True)
    maiden_name = models.CharField(max_length=1024, blank=True, null=True)
    date_added = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(Empprofile, models.DO_NOTHING, related_name='created_by')
    status = models.IntegerField(blank=True, null=True)
    document_date = models.DateField(blank=True, null=True)
    other_signature = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pas_service_record'


class PasServiceRecordData(models.Model):
    sr = models.ForeignKey('PasServiceRecord', on_delete=models.CASCADE)
    wh = models.ForeignKey(Workhistory, models.DO_NOTHING)
    poa = models.CharField(max_length=1024, blank=True, null=True)
    branch = models.CharField(max_length=255, blank=True, null=True)
    is_leave_wo_pay = models.BooleanField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    cause = models.CharField(max_length=255, blank=True, null=True)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    leave_w_pay_date = models.CharField(max_length=1024)

    class Meta:
        managed = False
        db_table = 'pas_service_record_data'