from django.contrib import admin

from .models import Adocao
from django.utils import timezone

@admin.register(Adocao)
class AdocaoAdmin(admin.ModelAdmin):
    list_display = ('animal', 'usuario', 'confirmado', 'data_pedido', 'data_confirmacao')
    actions = ['confirmar_adocao']

    def confirmar_adocao(self, request, queryset):
        for adocao in queryset:
            if not adocao.confirmado:
                adocao.confirmado = True
                adocao.data_confirmacao = timezone.now()
                adocao.save()
                # Muda status do animal
                adocao.animal.status = 'ADOTADO'
                adocao.animal.save()
        self.message_user(request, "Adoção(ões) confirmada(s) e animal(is) atualizado(s).")
    confirmar_adocao.short_description = "Confirmar adoção selecionada"
