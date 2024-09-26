from django.db import models
from django.utils import timezone

from backend.models import Empprofile


class CertTemplate(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    doctype = models.TextField(blank=True, null=True)
    is_iso = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'pas_cert_template'


class CertTransaction(models.Model):
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    content = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(Empprofile, models.DO_NOTHING, related_name='transaction_created_by')
    certtemp = models.ForeignKey('CertTemplate', models.DO_NOTHING)
    status = models.IntegerField(blank=True, null=True)
    cert_no = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'pas_cert_transaction'


class CertRequest(models.Model):
    tracking_no = models.CharField(max_length=255, blank=True, null=True)
    template = models.ForeignKey('CertTemplate', models.DO_NOTHING, blank=True, null=True)
    purpose = models.TextField(blank=True, null=True)
    date_of_filing = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cert_request'
