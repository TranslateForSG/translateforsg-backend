from rest_framework.pagination import PageNumberPagination


class PerPage100(PageNumberPagination):
    page_size = 1000
