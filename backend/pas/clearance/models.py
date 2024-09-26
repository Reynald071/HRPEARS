from django.db import models


class ClearanceContent(models.Model):
    content = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Clearance Content'
        managed = False
        db_table = 'clearance_content'


class ClearanceEmpstatus(models.Model):
    ccontent_id = models.IntegerField(blank=True, null=True)
    empstatus_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clearance_empstatus'