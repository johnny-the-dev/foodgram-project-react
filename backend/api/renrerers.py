from rest_framework_csv import renderers as r


class CSVCartRenderer (r.CSVRenderer):
    headers = ['Ингредиент', 'Количество']
