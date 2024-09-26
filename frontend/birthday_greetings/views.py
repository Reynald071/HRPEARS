from django.http import JsonResponse
from django.utils import timezone

from api.wiserv import send_sms_notification
from backend.models import Empprofile


def birthday_greetings(request, pk):
    if request.method == "GET":
        password = 'QRDHafgx6fsWb3cav9MEdD5Gvb6rayeJ'

        if pk == password:
            today = timezone.now().date()
            employee = Empprofile.objects.filter(pi__dob__day=today.day, pi__dob__month=today.month)

            for row in employee:
                msg = """
                    Happy Birthday, {}! I hope all your birthday wishes and
                    desires come true. We wish you a year full of minutes of love,
                    happines and joy - The My PORTAL Team
                    """.format(row.pi.user.first_name.title())

                send_sms_notification(msg, row.pi.mobile_no, 1, row.id)

            msg = send_sms_notification("Birthday Celebrants greeting have been sent.", "09287167193", 1, 1)

            return JsonResponse({'data': msg})
        else:
            return JsonResponse({'error': 'Invalid credentials'})
