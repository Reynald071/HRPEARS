import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
import django

django.setup()

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from suds.client import Client
from django.template.loader import get_template

# from backend.models import SMSLogs, Empprofile


def send_sms_notification(message, contact_number, emp_id, receiver_id=None):
    url = 'https://wiserv.dswd.gov.ph/soap/?wsdl'
    try:
        client = Client(url)
        result = client.service.sendMessage(UserName='crgwiservuser', PassWord='#w153rvcr9!', WSID='0',
                                           MobileNo=contact_number, Message=message)

        # if result:
        #     SMSLogs.objects.create(
        #         message=message,
        #         contact_number=contact_number,
        #         emp_id=emp_id,
        #         receiver_id=receiver_id if receiver_id else None
        #     )
        #
        #     return result
    except Exception:
        pass


def send_notification(message, contact_number, emp_id, receiver_id=None):
    try:
        employee = Empprofile.objects.filter(pi__mobile_no=contact_number).first()
        if employee.pi.user.email:
            plain_text = get_template('email_template/notify_me.txt')
            html_body = get_template('email_template/notify_me.html')

            subject = 'Caraga PORTAL'
            content = message
            email_from = settings.EMAIL_HOST_USER

            d = {
                'message': content,
            }

            message = EmailMultiAlternatives(
                subject,
                plain_text.render(d),
                email_from,
                [employee.pi.user.email]
            )

            message.attach_alternative(html_body.render(d), 'text/html')
            message.send(fail_silently=False)

            # client = Client(url)
            # result = client.service.sendMessage(UserName='crgwiservuser', PassWord='#w153rvcr9!', WSID='0',
            #                                    MobileNo=contact_number, Message=message)
            # if result:
            SMSLogs.objects.create(
                message=content,
                contact_number=contact_number,
                emp_id=emp_id,
                receiver_id=receiver_id if receiver_id else None
            )
    except Exception:
        pass


if __name__ == '__main__':
    send_sms_notification("Test", "09171063399", 1)
