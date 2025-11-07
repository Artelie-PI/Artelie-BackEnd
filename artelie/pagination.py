from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    # tamanho padrão por página
    page_size = 80
    # permite que o cliente ajuste o tamanho via query param: ?page_size=40
    page_size_query_param = "page_size"
    # limite máximo para não sobrecarregar o servidor
    max_page_size = 150
