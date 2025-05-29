from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'telefone', 'is_staff')
    # Apenas campos customizados no fieldset extra, não inclua date_joined nem last_login
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('telefone', 'profissao', 'estado_civil')}),
    )

admin.site.register(User, CustomUserAdmin)
