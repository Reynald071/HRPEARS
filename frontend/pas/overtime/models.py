import hashlib

from django.utils import timezone

from django.db import models

from backend.models import Empprofile, AuthUser


class OvertimeClaims(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pas_overtime_claims'


class OvertimeEmployee(models.Model):
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    detail = models.ForeignKey('OvertimeDetails', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'pas_overtime_employee'


def get_overtime_employee_others(detail_id):
    people = OvertimeEmployee.objects.filter(detail_id=detail_id).order_by('emp__pi__user__last_name')
    tresh = 5
    listofpeople = list()
    if people.count() > tresh:
        people = people[tresh:]
        for p in people:
            if '{} {}'.format(p.emp.pi.user.first_name.title(), p.emp.pi.user.last_name.title()) not in listofpeople:
                listofpeople.append('{} {}'.format(p.emp.pi.user.first_name.title(), p.emp.pi.user.last_name.title()))
    return '{}'.format(', '.join(listofpeople))


class OvertimeDetails(models.Model):
    overtime = models.ForeignKey('Overtime', models.DO_NOTHING)
    place = models.CharField(max_length=1024, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    nature_of_ot = models.TextField(blank=True, null=True)
    claims = models.ForeignKey('OvertimeClaims', models.DO_NOTHING)

    def get_employee(self):
        people = OvertimeEmployee.objects.filter(detail_id=self.id).order_by('emp__pi__user__last_name')
        if people.count() >= 5:
            others = 0
            tresh = 5
            listofpeople = list()
            if people.count() > tresh:
                others = people.count() - tresh
                people = people[:tresh]
            for p in people:
                if '{} {}'.format(p.emp.pi.user.first_name.title(), p.emp.pi.user.last_name.title()) not in listofpeople:
                    listofpeople.append('{} {}'.format(p.emp.pi.user.first_name.title(), p.emp.pi.user.last_name.title()))
            return '{}'.format(', '.join(
                listofpeople)) if others == 0 else '{}, and <span data-toggle="tooltip" data-html="true" data-placement="top" title="{}">{}</span> others..'.format(
                ', '.join(listofpeople), get_overtime_employee_others(self.id), others)
        else:
            employee_list = []
            for row in people:
                employee_list.append(row.emp.pi.user.get_fullname)

            if people.count() == 1:
                return "{}".format(employee_list[0])
            else:
                return "{}, and {}".format(",".join(str(row) for row in employee_list[:-1]), employee_list[-1])

    class Meta:
        managed = False
        db_table = 'pas_overtime_details'


def get_all_overtime_employee_others(detail_id):
    people = OvertimeEmployee.objects.filter(detail__overtime_id=detail_id).order_by('emp__pi__user__last_name')
    tresh = 5
    listofpeople = list()
    if people.count() > tresh:
        people = people[tresh:]
        for p in people:
            if '{} {}'.format(p.emp.pi.user.first_name.title(), p.emp.pi.user.last_name.title()) not in listofpeople:
                listofpeople.append('{} {}'.format(p.emp.pi.user.first_name.title(), p.emp.pi.user.last_name.title()))
    return '{}'.format(', '.join(listofpeople))


class Overtime(models.Model):
    tracking_no = models.CharField(max_length=255)
    prepared_by = models.ForeignKey(Empprofile, models.DO_NOTHING)
    date_requested = models.DateTimeField(default=timezone.now)
    approved_by = models.ForeignKey(Empprofile, models.DO_NOTHING, related_name="overtime_approved")
    approved_date = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)

    def get_hash_id(self):
        return hashlib.sha1(str(self.id).encode('utf-8')).hexdigest()

    def get_all_employee(self):
        people = OvertimeEmployee.objects.filter(detail__overtime_id=self.id).order_by('emp__pi__user__last_name')
        if people.count() >= 5:
            others = 0
            tresh = 5
            listofpeople = list()
            if people.count() > tresh:
                others = people.count() - tresh
                people = people[:tresh]
            for p in people:
                if '{} {}'.format(p.emp.pi.user.first_name.title(),
                                  p.emp.pi.user.last_name.title()) not in listofpeople:
                    listofpeople.append(
                        '{} {}'.format(p.emp.pi.user.first_name.title(), p.emp.pi.user.last_name.title()))
            return '{}'.format(', '.join(
                listofpeople)) if others == 0 else '{}, and <span data-toggle="tooltip" data-html="true" data-placement="top" title="{}">{}</span> others..'.format(
                ', '.join(listofpeople), get_all_overtime_employee_others(self.id), others)
        else:
            employee_list = []
            for row in people:
                employee_list.append(row.emp.pi.user.get_fullname)

            if people.count() == 1:
                return "{}".format(employee_list[0])
            else:
                return "{}, and {}".format(",".join(str(row) for row in employee_list[:-1]), employee_list[-1])

    class Meta:
        db_table = 'pas_overtime'