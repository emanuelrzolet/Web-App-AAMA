from django.urls import path
from .views import criar_adocao

urlpatterns = [
    path('api/adocao/', criar_adocao, name='criar_adocao'),
]
