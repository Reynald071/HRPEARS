import os
from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from django.contrib import admin

from backend.models import Empprofile, Empstatus
from portal.global_variables import count_leave_days


class LeaveType(models.Model):
    name = models.CharField(max_length=250)
    status = models.IntegerField(blank=True, null=True)

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.status == 1

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Leave Type'
        managed = False
        db_table = 'leave_type'


class LeaveSubtype(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()
    leavetype = models.ForeignKey(LeaveType, models.DO_NOTHING, verbose_name="Leave Type", blank=True, null=True)
    is_others = models.BooleanField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True, null=True)
    has_reason = models.BooleanField(blank=True, null=True)
    with_days = models.BooleanField(blank=True, null=True)
    remarks_text = models.CharField(max_length=255, blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.status == 1

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Leave Sub-Type'
        managed = False
        db_table = 'leave_subtype'


class LeaveSpent(models.Model):
    name = models.CharField(max_length=250)
    leavesubtype = models.ForeignKey(LeaveSubtype, models.DO_NOTHING, verbose_name="Leave Sub-Type")
    status = models.IntegerField(blank=True, null=True)
    is_specify = models.IntegerField(blank=True, null=True)

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.status == 1

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Leave Spent'
        verbose_name_plural = 'Leave Spent'
        managed = False
        db_table = 'leave_spent'


class LeavePrintLogs(models.Model):
    leaveapp = models.ForeignKey(LeaveType, models.DO_NOTHING)
    datetime = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'leave_print_logs'


class LeaveCredits(models.Model):
    leavetype = models.ForeignKey(LeaveType, models.DO_NOTHING)
    leave_total = models.DecimalField(max_digits=15, decimal_places=3, blank=True, null=True)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    updated_on = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'leave_credits'


class LeaveCreditHistory(models.Model):
    deduct_on = models.ForeignKey(LeaveType, models.DO_NOTHING)
    days = models.CharField(max_length=255, blank=True, null=True)
    application = models.ForeignKey('LeaveApplication', models.DO_NOTHING)
    remarks = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'leave_credits_history'


class LeaveApplication(models.Model):
    tracking_no = models.CharField(max_length=255, blank=True, null=True, unique=True)
    leavesubtype = models.ForeignKey(LeaveSubtype, models.DO_NOTHING)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    reasons = models.TextField(blank=True, null=True)
    date_of_filing = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    approved_date = models.DateTimeField()
    additional_remarks = models.TextField(blank=True, null=True)
    file = models.FileField(blank=True, null=True, upload_to='leave', default='leave/default.pdf')

    def get_latest_tracker_status(self):
        from tracker.models import TrackerPackageItem, TrackerPackageItemHistory
        package = TrackerPackageItem.objects.filter(leave_tracking_no=self.tracking_no)
        if package:
            data = TrackerPackageItemHistory.objects.filter(package_id=package.first().id).order_by('-id')
            if data:
                return data.first().status.name
        else:
            return 'Pending'

    def get_inclusive(self):
        if self.start_date:
            if self.start_date == self.end_date:
                return self.start_date.strftime("%B %d, %Y")
            else:
                if not self.end_date:
                    return "{}".format(self.start_date.strftime("%B %d, %Y"))
                else:
                    return "{} - {}".format(self.start_date.strftime("%B %d, %Y"), self.end_date.strftime("%B %d, %Y"))
        else:
            leave_dates = LeaveRandomDates.objects.filter(leaveapp_id=self.id)
            if leave_dates:
                if leave_dates.count() != 1:
                    random_dates = []
                    for row in leave_dates:
                        random_dates.append(row.date.strftime("%B %d, %Y"))

                    text = "{} and {}".format(", ".join(str(row) for row in random_dates[:-1]), random_dates[-1])
                    return text
                else:
                    random_dates = []
                    for row in leave_dates:
                        random_dates.append(row.date.strftime("%B %d, %Y"))

                    text = "{}".format(random_dates[0])
                    return text
            else:
                return self.remarks

    def get_leave_delays(self):
        content = ""
        days = 0
        if self.start_date:
            days = count_leave_days(self.date_of_filing, self.start_date)
        else:
            leave_dates = LeaveRandomDates.objects.filter(leaveapp_id=self.id)
            if leave_dates:
                random_dates = []
                for row in leave_dates:
                    random_dates.append(row.date)

                days = count_leave_days(self.date_of_filing, random_dates[0])

        if days > 1:
            content += '<span class="badge bg-warning">delayed for {} days</span>'.format(days)
        elif days == 1:
            content += '<span class="badge bg-warning">delayed for {} day</span>'.format(days)
        else:
            content += ''

        return content

    class Meta:
        db_table = 'leave_application'


@receiver(models.signals.pre_save, sender=LeaveApplication)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = LeaveApplication.objects.get(pk=instance.pk).file
    except LeaveApplication.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class LeavespentApplication(models.Model):
    leaveapp = models.ForeignKey(LeaveApplication, on_delete=models.CASCADE)
    leavespent = models.ForeignKey(LeaveSpent, models.DO_NOTHING, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    specify = models.TextField(blank=True, null=True)

    def get_start_date(self):
        if self.leaveapp.start_date:
            return self.leaveapp.start_date

    def get_random_dates(self):
        random_dates = LeaveRandomDates.objects.values_list('date', flat=True).filter(leaveapp_id=self.leaveapp_id)
        return random_dates

    def get_leave_status(self):
        if self.leaveapp.status == 0:
            return "Pending"
        elif self.leaveapp.status == 1:
            return "Approved"
        elif self.leaveapp.status == 2:
            return "Cancel"

    def get_leave_reasons(self):
        if self.leaveapp.reasons:
            return self.leaveapp.reasons
        else:
            return self.specify

    class Meta:
        db_table = 'leavespent_application'


class LeaveRandomDates(models.Model):
    leaveapp = models.ForeignKey(LeaveApplication, on_delete=models.CASCADE)
    date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'leave_random_dates'


class CTDORequests(models.Model):
    tracking_no = models.CharField(max_length=255, blank=True, null=True)
    date_filed = models.DateTimeField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    status = models.IntegerField()
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    drn = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='ctdo', blank=True, null=True, default='ctdo/default.pdf')
    coc_filed = models.DateField(blank=True, null=True)

    def get_latest_tracker_status(self):
        from tracker.models import TrackerPackageItem, TrackerPackageItemHistory
        package = TrackerPackageItem.objects.filter(leave_tracking_no=self.tracking_no)
        if package:
            data = TrackerPackageItemHistory.objects.filter(package_id=package.first().id).order_by('-id')
            if data:
                return data.first().status.name
        else:
            return 'Pending'

    def get_inclusive(self):
        if self.start_date:
            if self.start_date == self.end_date:
                return self.start_date.strftime("%B %d, %Y")
            else:
                if not self.end_date:
                    return "{}".format(self.start_date.strftime("%B %d, %Y"))
                else:
                    return "{} - {}".format(self.start_date.strftime("%B %d, %Y"),
                                            self.end_date.strftime("%B %d, %Y"))
        else:
            ctdo_dates = CTDORandomDates.objects.filter(ctdo_id=self.id)
            if ctdo_dates:
                if ctdo_dates.count() != 1:
                    random_dates = []
                    for row in ctdo_dates:
                        random_dates.append(row.date.strftime("%B %d, %Y"))

                    text = "{} and {}".format(", ".join(str(row) for row in random_dates[:-1]), random_dates[-1])
                    return text
                else:
                    random_dates = []
                    for row in ctdo_dates:
                        random_dates.append(row.date.strftime("%B %d, %Y"))

                    text = "{}".format(random_dates[0])
                    return text

    class Meta:
        db_table = 'ctdo_requests'


@receiver(models.signals.pre_save, sender=CTDORequests)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = CTDORequests.objects.get(pk=instance.pk).file
    except LeaveApplication.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class CTDOPrintLogs(models.Model):
    ctdo = models.ForeignKey('CTDORequests', models.DO_NOTHING)
    datetime = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'ctdo_print_logs'


class CTDORandomDates(models.Model):
    ctdo = models.ForeignKey('CTDORequests', models.DO_NOTHING)
    date = models.DateField(blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'ctdo_random_dates'


class LeaveSignatory(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    designation = models.CharField(max_length=255, blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)
    classes = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'leave_signatory'


class LeavePermissions(models.Model):
    leavesubtype = models.ForeignKey(
        LeaveSubtype, models.DO_NOTHING, blank=True, null=True, verbose_name='Leave Sub-Type'
    )
    empstatus_id = models.IntegerField(blank=True, null=True)

    @admin.display(description='Employee status')
    def display_empstatus(self):
        return Empstatus.objects.filter(id=self.empstatus_id).first()

    class Meta:
        managed = False
        verbose_name = 'Leave Permission'
        verbose_name_plural = 'Leave Permissions'
        db_table = 'leave_permissions'


class CTDOBalance(models.Model):
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    days = models.FloatField(blank=True, null=True)
    hours = models.FloatField(blank=True, null=True)
    minutes = models.FloatField(blank=True, null=True)
    date_expiry = models.DateField(blank=True, null=True)
    month_earned = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ctdo_balance'


class CTDOActualBalance(models.Model):
    cocbal = models.ForeignKey('CTDOBalance', models.DO_NOTHING)
    days = models.FloatField(blank=True, null=True)
    hours = models.FloatField(blank=True, null=True)
    minutes = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ctdo_actual_balance'


class CTDOUtilization(models.Model):
    ctdoreq = models.ForeignKey('CTDORequests', models.DO_NOTHING, blank=True, null=True)
    days = models.FloatField(blank=True, null=True)
    hours = models.FloatField(blank=True, null=True)
    minutes = models.FloatField(blank=True, null=True)
    cocactualbal = models.ForeignKey('CTDOActualBalance', models.DO_NOTHING)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'ctdo_utilization'


class CTDOHistoryBalance(models.Model):
    ctdoreq = models.ForeignKey('CTDORequests', models.DO_NOTHING)
    total_days = models.IntegerField(blank=True, null=True)
    total_hours = models.IntegerField(blank=True, null=True)
    total_minutes = models.IntegerField(blank=True, null=True)
    total_u_days = models.IntegerField(blank=True, null=True)
    total_u_hours = models.IntegerField(blank=True, null=True)
    total_u_minutes = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ctdo_history_balance'


class CTDOCoc(models.Model):
    ctdoreq = models.ForeignKey('CTDORequests', models.DO_NOTHING)
    month_earned = models.CharField(max_length=255, blank=True, null=True)
    days = models.IntegerField(blank=True, null=True)
    hours = models.IntegerField(blank=True, null=True)
    minutes = models.IntegerField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'ctdo_coc'


