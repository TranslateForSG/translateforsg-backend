from rest_framework.pagination import PageNumberPagination


class PerPage100(PageNumberPagination):
    page_size = 100


class PerPage1000(PageNumberPagination):
    page_size = 1000
