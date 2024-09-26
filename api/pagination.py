from rest_framework.pagination import PageNumberPagination


class LargeSetPagination(PageNumberPagination):
    page_size = 100


class SmallSetPagination(PageNumberPagination):
    page_size = 10