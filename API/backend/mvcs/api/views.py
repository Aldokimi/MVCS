from rest_framework.response import Response
from rest_framework.decorators import api_view


from core.models import Repository, Branch, Commit


@api_view(['GET'])
def get_data(request):
    person = {
        'name':'doki',
        'age':15, 
    }
    return Response(person)
