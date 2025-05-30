# Generated by Django 5.0.2 on 2025-05-29 00:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Adocao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_pedido', models.DateTimeField(auto_now_add=True)),
                ('data_confirmacao', models.DateTimeField(blank=True, null=True)),
                ('confirmado', models.BooleanField(default=False)),
                ('animal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='adocoes', to='core.animal')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='adocoes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
