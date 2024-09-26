from django.db import models

from backend.models import Empprofile


class LeaveCertificationType(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(blank=True, null=True)
    template = models.TextField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    document_no = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pas_leave_certification_type'


class LeaveCertificationTransaction(models.Model):
    drn = models.CharField(max_length=255)
    date_created = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(Empprofile, models.DO_NOTHING)
    content = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=255)
    forwarded_to = models.ForeignKey(Empprofile, models.DO_NOTHING, related_name='forwarded_to')
    type = models.ForeignKey('LeaveCertificationType', models.DO_NOTHING)
    emp_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pas_leave_certification_transaction'
