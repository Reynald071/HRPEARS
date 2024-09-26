from django.core.management.base import BaseCommand

from frontend.models import DeskServices, DeskServicesAdInfo


class Command(BaseCommand):
    help = 'Create auto acknowledgement receipt'

    def handle(self, *args, **kwargs):
        services = DeskServices.objects.all()

        for row in services:
            try:
                message = f"""
                    Dear {row.requested_by.pi.user.first_name.title()} <br><br>
                    We've received your request for {row.classification.name.title()}<br><br>
                    Your concern is currently under review, and once approved, we will promptly send it to you. <br><br>
                    Thank you for your patience. <br><br>
                    Sincerely, <br>
                    The {row.assigned_emp.section.sec_acronym}-Caraga
                """.strip()

                # DeskServicesAdInfo.objects.create(
                #     services_id=row.id,
                #     description=message,
                #     emp_id=row.assigned_emp_id,
                #     date_sent=row.date_time,
                #     is_read=1
                # )

                print(message)
            except Exception as e:
                print("Error in {}".format(e))