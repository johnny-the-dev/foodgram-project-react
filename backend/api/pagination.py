from collections import OrderedDict
from rest_framework import pagination, status
from rest_framework.response import Response


class PageNumberLimitPagination(pagination.PageNumberPagination):
    page_size_query_param = 'limit'


class SubscriptionsPagination(pagination.PageNumberPagination):
    page_size_query_param = 'limit'
    recipes_limit_query = 'recipes_limit'
    
    def get_paginated_response(self, data):
        recipes_limit = self.request.query_params.get(self.recipes_limit_query)
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
            except ValueError:
                return Response({'error: ': 'recipes_limit должно быть целым числом.'}, status=status.HTTP_400_BAD_REQUEST)
            for author in data:
                author['recipes'] = author['recipes'][:recipes_limit]
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))