from django.db import models

from django.conf import settings

class Adocao(models.Model):
    animal = models.ForeignKey('core.Animal', on_delete=models.CASCADE, related_name='adocoes')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='adocoes')
    data_pedido = models.DateTimeField(auto_now_add=True)
    data_confirmacao = models.DateTimeField(null=True, blank=True)
    confirmado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.usuario} -> {self.animal} ({'Confirmada' if self.confirmado else 'Pendente'})"
