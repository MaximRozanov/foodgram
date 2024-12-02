from foodgram_backend.constants import PER_PAGE_LIMIT
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = PER_PAGE_LIMIT
