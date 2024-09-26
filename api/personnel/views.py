from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_tracking.mixins import LoggingMixin

from api.pagination import LargeSetPagination, SmallSetPagination
from api.personnel.serializers import MOTSerializer, RitodetailsSerializer, RitoPeopleSerializer, EmployeeSerializer, \
    PositionSerializer, LeaveSpentApplicationSerializer
from backend.libraries.leave.models import LeavespentApplication
from backend.models import Empprofile, Position
from frontend.models import Mot, Ritodetails, Ritopeople


class LeaveDetailsView(LoggingMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        id_number = request.GET.get('id_number', '')
        queryset = LeavespentApplication.objects.filter(leaveapp__emp__id_number=id_number)
        serializer = LeaveSpentApplicationSerializer(queryset, many=True)
        return Response(serializer.data)


class MOTView(LoggingMixin, generics.ListAPIView):
    queryset = Mot.objects.filter(status=1).order_by('name')
    serializer_class = MOTSerializer
    pagination_class = SmallSetPagination
    permission_classes = [IsAuthenticated]


class RitoDetailsView(LoggingMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = request.GET.get('q', '')
        travel_id = request.GET.get('travel_id', '')
        status = request.GET.get('status', '')
        if q:
            queryset = Ritodetails.objects.filter(Q(rito__status__in=[2, 3]),
                                                  Q(place__icontains=q) |
                                                  Q(purpose__icontains=q) |
                                                  Q(expected_output__icontains=q) |
                                                  Q(rito__tracking_no__icontains=q) |
                                                  Q(inclusive_from__icontains=q) |
                                                  Q(inclusive_to__icontains=q)).order_by('-rito__tracking_no')

            paginator = SmallSetPagination()
            result_page = paginator.paginate_queryset(queryset, request)
            serializer = RitodetailsSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        elif travel_id:
            queryset = Ritodetails.objects.filter(Q(id=travel_id), Q(rito__status__in=[2, 3])).order_by('-rito__tracking_no')
            serializer = RitodetailsSerializer(queryset, many=True)
            return Response(serializer.data)
        elif status:
            queryset = Ritodetails.objects.filter(Q(rito__status__in=[2, 3]),
                                                  Q(rito__status=2 if status == "Pending" else 3 if status == "Approved" else 0)).order_by('-rito__tracking_no')
            paginator = SmallSetPagination()
            result_page = paginator.paginate_queryset(queryset, request)
            serializer = RitodetailsSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        else:
            queryset = Ritodetails.objects.filter(Q(rito__status__in=[2, 3])).order_by('-rito__tracking_no')

            paginator = SmallSetPagination()
            result_page = paginator.paginate_queryset(queryset, request)
            serializer = RitodetailsSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)


class RitoPeopleView(LoggingMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        travel_id = request.GET.get('travel_id', '')
        tracking_number = request.GET.get('tracking_number', '')
        if tracking_number:
            rito = Ritopeople.objects.filter(detail__rito__tracking_no=tracking_number)
        else:
            rito = Ritopeople.objects.filter(detail_id=travel_id)
        serializer = RitoPeopleSerializer(rito, many=True)
        return Response(serializer.data)


class UpdateTravelMOTView(LoggingMixin, APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        details = Ritodetails.objects.filter(id=request.GET.get('travel_id', ''))
        if details:
            Ritodetails.objects.filter(id=request.GET.get('travel_id', '')).update(
                mot_id=request.GET.get('mot_id', '')
            )
            return Response({"success": {
                "code": 200,
                "message": "Travel details successfully updated."
            }}, status=status.HTTP_200_OK)
        else:
            return Response({"error": {
                "code": 404,
                "message": "Travel details not found."
            }}, status=status.HTTP_404_NOT_FOUND)


class PositionView(LoggingMixin, generics.ListAPIView):
    queryset = Position.objects.filter(status=1).order_by('name')
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]


class EmployeeDetailsView(LoggingMixin, generics.ListAPIView):
    queryset = Empprofile.objects.filter(pi__user__is_active=1).order_by('pi__user__last_name')
    serializer_class = EmployeeSerializer
    pagination_class = LargeSetPagination
    permission_classes = [IsAuthenticated]


class EmployeeDetailsLoadView(LoggingMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Empprofile.objects.filter(pi__user__is_active=1).order_by('pi__user__last_name')
        serializer = EmployeeSerializer(queryset, many=True)
        return Response(serializer.data)


class SearchEmployeeView(LoggingMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = request.GET.get('q', '')
        employee = Empprofile.objects.filter(Q(section__sec_name__icontains=q) |
                                            Q(id_number__icontains=q) |
                                            Q(position__name__icontains=q) |
                                            Q(pi__user__username__icontains=q) |
                                             Q(pi__user__first_name__icontains=q) |
                                             Q(pi__user__last_name__icontains=q) |
                                             Q(pi__user__middle_name__icontains=q)).order_by('pi__user__last_name')
        serializer = EmployeeSerializer(employee, many=True)
        return Response(serializer.data)




