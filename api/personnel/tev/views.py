from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.personnel.tev.serializers import TevSerializers
from backend.models import Empprofile
from backend.templatetags.tags import force_token_decryption, generate_token
from frontend.pas.tev.models import TransNamelist


def get_infimos_db(value):
    dataset = {
        '2020': 'infimos20',
        '2021': 'infimos21',
        '2022': 'infimos22',
        '2023': 'infimos23',
    }

    return dataset[value]


class TevTrackerView(generics.ListAPIView):
    serializer_class = TevSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.query_params.get('pk'):
            year = self.request.query_params.get('year')
            id_number = force_token_decryption(self.request.query_params.get('pk'))
            queryset = TransNamelist.objects.using(str(get_infimos_db(year))).filter(transaction__transaction__dv_date__year=year,
                                                                                     id_number=id_number)

            return queryset
        elif self.request.query_params.get('section_pk') == generate_token(1):
            year = self.request.query_params.get('year')
            queryset = TransNamelist.objects.using(str(get_infimos_db(year))).filter(
                transaction__transaction__dv_date__year=year,
                id_number__in=[row.id_number for row in Empprofile.objects.filter(section_id=1)])

            return queryset