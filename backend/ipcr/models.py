from django.db import models
from django.utils import timezone

from backend.documents.models import Docs201Files
from backend.models import Empprofile


class IPC_Rating(models.Model):
    year = models.IntegerField(blank=True, null=True)
    semester = models.IntegerField(blank=True, null=True)
    ipcr = models.FloatField(blank=True, null=True)
    file = models.ForeignKey(Docs201Files, on_delete=models.CASCADE, blank=True, null=True)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    date_added = models.DateTimeField(default=timezone.now)

    @property
    def get_file(self):
        if self.file_id:
            return "<span class='label label-success'>Attachment</span>"
        else:
            return "<span class='label label-default'>Attachments can be found in the 201 files</span>"

    class Meta:
        managed = False
        db_table = 'ipc_rating'


class IPC_AdjectivalRating(models.Model):
    start_average = models.FloatField(blank=True, null=True)
    end_average = models.FloatField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ipc_adjectival_rating'