from django.db import models

from backend.models import Empprofile, Position, Empstatus, Fundsource


class PasEndorsementPeople(models.Model):
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    position = models.ForeignKey(Position, models.DO_NOTHING)
    basic_salary = models.CharField(max_length=255, blank=True, null=True)
    premium_rate = models.CharField(max_length=255, blank=True, null=True)
    effectivity_contract = models.DateField(blank=True, null=True)
    end_of_contract = models.DateField(blank=True, null=True)
    empstatus = models.ForeignKey(Empstatus, models.DO_NOTHING)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    fundcharge = models.ForeignKey(Fundsource, models.DO_NOTHING)
    vice = models.CharField(max_length=1024, blank=True, null=True)
    vice_id_number = models.CharField(max_length=10, blank=True, null=True)
    endorsement_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pas_endorsement_people'


def get_all_people_others(endorsement_id):
    people = PasEndorsementPeople.objects.filter(endorsement_id=endorsement_id).order_by('emp__pi__user__last_name')
    tresh = 5
    listofpeople = list()
    if people.count() > tresh:
        people = people[tresh:]
        for p in people:
            if p.emp.pi.user.get_fullname not in listofpeople:
                listofpeople.append(p.emp.pi.user.get_fullname)
    return '{}'.format(', '.join(listofpeople))


class PasEndorsement(models.Model):
    date = models.DateField(blank=True, null=True)
    preparedby = models.ForeignKey(Empprofile, models.DO_NOTHING)

    @property
    def get_all_people(self):
        people = PasEndorsementPeople.objects.filter(endorsement_id=self.id).order_by('emp__pi__user__last_name')
        if people.count() >= 5:
            others = 0
            tresh = 5
            listofpeople = list()
            if people.count() > tresh:
                others = people.count() - tresh
                people = people[:tresh]
            for p in people:
                if p.emp.pi.user.get_fullname not in listofpeople:
                    listofpeople.append(p.emp.pi.user.get_fullname)
            return '{}'.format(', '.join(
                listofpeople)) if others == 0 else '{}, and <span data-toggle="tooltip" data-html="true" data-placement="top" title="{}">{}</span> others..'.format(
                ', '.join(listofpeople), get_all_people_others(self.id), others)
        else:
            employee_list = []
            for row in people:
                employee_list.append(row.emp.pi.user.get_fullname)

            if employee_list:
                if people.count() == 1:
                    return "{}".format(employee_list[0])
                else:
                    return "{}, and {}".format(",".join(str(row) for row in employee_list[:-1]), employee_list[-1])

    class Meta:
        managed = False
        db_table = 'pas_endorsement'