import os
from django.db import models


class RsoType(models.Model):
    name = models.CharField(max_length=1024, blank=True, null=True)

    class Meta:
        db_table = 'rso_type'


class RsoAttachment(models.Model):
    year = models.CharField(max_length=255, blank=True, null=True)
    rso_no = models.CharField(max_length=255, blank=True, null=True)
    type = models.ForeignKey('RsoType', models.DO_NOTHING)
    title = models.CharField(max_length=1024, blank=True, null=True)
    attachment = models.FileField(upload_to='rso')
    date_uploaded = models.DateTimeField(blank=True, null=True)

    @property
    def get_filename(self):
        return os.path.basename(self.attachment.name)

    class Meta:
        db_table = 'rso_attachment'