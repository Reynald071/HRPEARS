from django.db import models
from django.utils import timezone

from backend.models import Empprofile


class IsoDownloadhistory(models.Model):
    downloaded_on = models.DateField(default=timezone.now)
    form = models.ForeignKey('IsoForms', models.DO_NOTHING)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'iso_downloadhistory'


class IsoForms(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    attachment = models.FileField(upload_to='iso/forms/%Y/%m')
    document_no = models.CharField(max_length=255, unique=True)
    revision_no = models.IntegerField(blank=True, null=True)
    uploaded_on = models.DateField(blank=True, null=True)
    uploaded_by = models.ForeignKey(Empprofile, models.DO_NOTHING)
    is_active = models.BooleanField()
    is_deleted = models.BooleanField()
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'iso_forms'
