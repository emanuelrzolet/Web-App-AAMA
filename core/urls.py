from django.urls import path
from django.contrib.auth import views as auth_vi8ews
from . import views
from .views_api import tem_perfil_adotante

urlpatterns = [
    path('get_cores/', views.get_cores, name='get_cores'),
    path('', views.home, name='home'),
    path('adotar/', views.animal_list, name='animal_list'),
    path("donate/", views.donate, name='donate'),
    path("about/", views.about, name='about'),
    path("volunteering/", views.volunteering, name='volunteering'),
    path('nfc', views.nfc, name='nfc'),
    path('animal/<int:pk>/', views.animal_detail, name='animal_detail'),
    path('api/animals/', views.load_animals, name='load_animals'),
    path('api/racas/', views.get_racas, name='get_racas'),
    path('api/adocao/', views.create_adocao, name='create_adocao'),
    path('api/tem_perfil_adotante/', tem_perfil_adotante, name='tem_perfil_adotante'),
    
    # Authentication URLs are handled by django-allauth through /accounts/
    path('animal/list/', views.animal_list, name='animal_list'),
    path('add_raca_cachorro/', views.add_raca_cachorro, name='add_raca_cachorro'),
    path('add_raca_gato/', views.add_raca_gato, name='add_raca_gato'),
    path('animal/<int:animal_id>/toggle-like/', views.toggle_like, name='toggle_like'),
    path('animal/<int:animal_id>/is-liked/', views.is_animal_liked, name='is_animal_liked'),
] 