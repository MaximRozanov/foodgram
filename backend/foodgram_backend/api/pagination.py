from rest_framework.pagination import PageNumberPagination

from foodgram_backend.constants import PER_PAGE_LIMIT


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = PER_PAGE_LIMIT
