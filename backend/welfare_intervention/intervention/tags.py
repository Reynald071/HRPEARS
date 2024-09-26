from django import template
from django.db.models import Count
from backend.models import Empprofile
from django.db.models import Q
from backend.welfare_intervention.intervention.models import sweap_assistance, CovidAssistance
from datetime import date

register = template.Library()
today = date.today()

@register.simple_tag
def getallempdata(id_number):
	empname = Empprofile.objects.filter(id_number=id_number).all()
	return empname


@register.simple_tag
def duplicate(emp_id):
	emp_id = sweap_assistance.objects.filter(emp_id=emp_id)
	if emp_id.count() > 1:
		return True
	else:
		return False

@register.simple_tag
def dates(end):
	if end == today:
		emp_id = CovidAssistance.objects.filter(end=today)
		return emp_id

