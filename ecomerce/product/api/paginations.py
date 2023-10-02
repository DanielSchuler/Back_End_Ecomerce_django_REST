from rest_framework.pagination import PageNumberPagination


'''
FOR MORE INFORMATION ON THE PRODUCTPAGINATION LOOK IN THE VIEW_EXPLANATION.TXT
'''
class ProductPagination(PageNumberPagination):
    page_size = 3
    page_query_param = 'p'
    page_size_query_param = 'size'
    max_page_size = 3
    last_page_strings = ['end']