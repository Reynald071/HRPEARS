from django.db import models


class DTRAssignee(models.Model):
    emp = models.ForeignKey('Empprofile', models.DO_NOTHING)
    assigned = models.ForeignKey('Empprofile', models.DO_NOTHING, related_name='assigned')
    date_assigned = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dtr_assignee'