from django.db import models

from django.conf import settings

class Adocao(models.Model):
    animal = models.ForeignKey('core.Animal', on_delete=models.CASCADE, related_name='adocoes')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='adocoes')
    data_pedido = models.DateTimeField(auto_now_add=True)
    data_confirmacao = models.DateTimeField(null=True, blank=True)
    confirmado = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        from django.utils import timezone
        confirmado_antes = None
        if self.pk:
            confirmado_antes = type(self).objects.get(pk=self.pk).confirmado
        # Se está confirmando agora
        if self.confirmado and (not confirmado_antes):
            self.data_confirmacao = self.data_confirmacao or timezone.now()
            super().save(*args, **kwargs)
            self.animal.status = 'ADOTADO'
            self.animal.saida_instituicao = self.data_confirmacao
            self.animal.save()
        # Se está cancelando a confirmação
        elif not self.confirmado and confirmado_antes:
            self.data_confirmacao = None
            super().save(*args, **kwargs)
            self.animal.status = 'DISPONIVEL'
            self.animal.saida_instituicao = None
            self.animal.save()
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario} -> {self.animal} ({'Confirmada' if self.confirmado else 'Pendente'})"
