from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('adotar/', views.animal_list, name='animal_list'),
    path('animal/<int:pk>/', views.animal_detail, name='animal_detail'),
    path('api/animals/', views.load_animals, name='load_animals'),
    path('api/adocao/', views.create_adocao, name='create_adocao'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='core/registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # Password Reset URLs
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(template_name='core/registration/password_reset_form.html'),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='core/registration/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='core/registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='core/registration/password_reset_complete.html'),
         name='password_reset_complete'),
] 