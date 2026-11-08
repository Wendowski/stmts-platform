import json
from pathlib import Path
from uuid import UUID
from django.conf import settings
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response

FIXTURE = Path(__file__).resolve().parents[2] / 'contracts/fixtures/post.json'
@api_view(['GET'])
def post(request, post_id):
    # Fixture API is deliberately unavailable outside explicit development mode.
    if not settings.DEBUG:
        return Response({'code':'UNAVAILABLE','message':'Statement unavailable','requestId':'read-only'},status=404)
    data=json.loads(FIXTURE.read_text())
    if str(post_id)!=data['id']:
        return Response({'code':'UNAVAILABLE','message':'Statement unavailable','requestId':'read-only'},status=404)
    response=Response(data)
    response['Cache-Control']='no-store'
    return response
urlpatterns=[path('v1/posts/<uuid:post_id>',post)]
