from django.db import models

from backend.models import Empprofile


class DocsCopy(models.Model):
    id_number = models.CharField(max_length=11, blank=True, null=True)
    doc_track = models.ForeignKey('DocsTrackingInfo', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'docs_copy'


class DocsTrackingInfo(models.Model):
    tracking_no = models.CharField(max_length=50, blank=True, null=True)
    from_field = models.CharField(db_column='from', max_length=100, blank=True, null=True)  # Field renamed because it was a Python reserved word.
    origin = models.CharField(max_length=255, blank=True, null=True)
    document_type = models.ForeignKey('DocsType', models.DO_NOTHING)
    subject = models.CharField(max_length=100, blank=True, null=True)
    purpose = models.CharField(max_length=150, blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    date_received = models.DateTimeField(blank=True, null=True)
    date_added = models.DateTimeField(blank=True, null=True)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'docs_tracking_info'


class DocsTrackingStatus(models.Model):
    doc_info = models.ForeignKey('DocsTrackingInfo', models.DO_NOTHING)
    trail = models.ForeignKey('DocsTrail', models.DO_NOTHING)
    remarks = models.TextField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    id_number = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'docs_tracking_status'


class DocsType(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    uploaded_by_id = models.IntegerField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'docs_type'


class DocsTrail(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'docs_trail'


class DocsScope(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'docs_scope'