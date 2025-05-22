from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from .forms import AnimalTypeForm, AnimalForm, CachorroForm, GatoForm
from .models import (
    User, Animal, Cachorro, Gato, 
    RacaCachorro, RacaGato, Adocao, 
    Dose, Vacinas, Endereco, FotoAnimal
)

class FotoAnimalInline(admin.TabularInline):
    model = FotoAnimal
    extra = 1
    fields = ('foto', 'is_principal')

class CachorroInline(admin.StackedInline):
    model = Cachorro
    can_delete = False
    verbose_name = 'Informações do Cachorro'
    verbose_name_plural = 'Informações do Cachorro'
    form = CachorroForm

class GatoInline(admin.StackedInline):
    model = Gato
    can_delete = False
    verbose_name = 'Informações do Gato'
    verbose_name_plural = 'Informações do Gato'
    form = GatoForm

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    form = AnimalForm
    list_display = ('nome', 'tipo', 'genero', 'comportamento', 'status', 'idade_display', 'pertence_instituicao', 'preview_foto')
    list_filter = ('tipo', 'comportamento', 'status', 'pertence_instituicao')
    search_fields = ('nome',)
    readonly_fields = ('idade_display', 'preview_foto', 'add_cor', 'add_raca_cachorro', 'add_raca_gato')
    inlines = [FotoAnimalInline]

    class Media:
        css = {
            'all': (
                'admin/css/forms.css',
                'admin/css/custom.css',
            )
        }
        js = (
            'admin/js/jquery.init.js',
            'admin/js/core.js',
            'js/animal_admin.js',
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['tipo'].widget.attrs['readonly'] = True
        return form

    def get_fieldsets(self, request, obj=None):
        # Get the tipo from either the object, POST data, or GET parameters
        tipo = None
        if obj:
            tipo = obj.tipo
        elif request.method == 'POST':
            tipo = request.POST.get('tipo')
        elif request.method == 'GET':
            tipo = request.GET.get('tipo')

        # Base fieldsets that are always shown
        fieldsets = [
            ('Informações Básicas', {
                'fields': (('nome', 'tipo'), ('cor', 'add_cor')),
                'classes': ('wide',)
            }),
        ]

        # Add type-specific fieldsets based on the selected tipo
        if tipo == 'CACHORRO':
            fieldsets.append(('Informações do Cachorro', {
                'fields': (('raca_cachorro', 'add_raca_cachorro'), 'porte'),
                'classes': ('wide',)
            }))
        elif tipo == 'GATO':
            fieldsets.append(('Informações do Gato', {
                'fields': (('raca_gato', 'add_raca_gato'),),
                'classes': ('wide',)
            }))

        # Add remaining common fieldsets
        fieldsets.extend([
            ('Idade', {
                'fields': ('dataNascimento', 'idadeEstimada', 'idade_display'),
                'classes': ('wide',),
                'description': 'Preencha a data de nascimento OU a idade estimada. O sistema calculará automaticamente o outro campo.'
            }),
            ('Características', {
                'fields': ('comportamento', 'pelagem', 'genero', 'castrado'),
                'classes': ('wide',)
            }),
            ('Descrição', {
                'fields': ('descricao',),
                'classes': ('wide',),
                'description': 'Adicione informações sobre o animal, seu comportamento, história, etc.'
            }),
            ('Status', {
                'fields': ('status', 'pertence_instituicao', 'saida_instituicao', 'entrada_instituicao'),
                'classes': ('wide',)
            }),
        ])

        return fieldsets

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # Handle type-specific data
        if obj.tipo == 'CACHORRO':
            raca = form.cleaned_data.get('raca_cachorro')
            porte = form.cleaned_data.get('porte')
            
            if not hasattr(obj, 'cachorro'):
                # Create new Cachorro instance
                Cachorro.objects.create(
                    animal=obj,
                    raca=raca or RacaCachorro.get_default_raca(),
                    porte=porte or 2
                )
            else:
                # Update existing Cachorro instance
                obj.cachorro.raca = raca or RacaCachorro.get_default_raca()
                obj.cachorro.porte = porte or 2
                obj.cachorro.save()
                
        elif obj.tipo == 'GATO':
            raca = form.cleaned_data.get('raca_gato')
            
            if not hasattr(obj, 'gato'):
                # Create new Gato instance
                Gato.objects.create(
                    animal=obj,
                    raca=raca or RacaGato.get_default_raca()
                )
            else:
                # Update existing Gato instance
                obj.gato.raca = raca or RacaGato.get_default_raca()
                obj.gato.save()

    def preview_foto(self, obj):
        if obj.foto_principal:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.foto_principal.url)
        return "Sem foto"
    preview_foto.short_description = "Foto Principal"
    
    def idade_display(self, obj):
        if obj.dataNascimento:
            return f"{obj.calcular_idade()} anos"
        elif obj.idadeEstimada:
            return f"{obj.idadeEstimada} anos (estimado)"
        return "Idade não informada"
    idade_display.short_description = "Idade"

    def add_cor(self, obj):
        return format_html(
            '''
            <button type="button" class="button" onclick="return showColorDialog();">
                Adicionar Nova Cor
            </button>
            '''
        )
    add_cor.short_description = ""

    def add_raca_cachorro(self, obj):
        return format_html(
            '''
            <button type="button" class="button" onclick="return showBreedDialog('cachorro');">
                Adicionar Nova Raça
            </button>
            '''
        )
    add_raca_cachorro.short_description = ""

    def add_raca_gato(self, obj):
        return format_html(
            '''
            <button type="button" class="button" onclick="return showBreedDialog('gato');">
                Adicionar Nova Raça
            </button>
            '''
        )
    add_raca_gato.short_description = ""

@admin.register(FotoAnimal)
class FotoAnimalAdmin(admin.ModelAdmin):
    list_display = ('animal', 'is_principal', 'data_upload', 'preview_foto')
    list_filter = ('is_principal', 'data_upload')
    search_fields = ('animal__nome',)
    
    def preview_foto(self, obj):
        if obj.foto:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.foto.url)
        return "Sem foto"
    preview_foto.short_description = "Preview"

@admin.register(RacaCachorro)
class RacaCachorroAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(RacaGato)
class RacaGatoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Cachorro)
class CachorroAdmin(admin.ModelAdmin):
    list_display = ('animal', 'raca', 'porte')
    list_filter = ('porte', 'raca')
    search_fields = ('animal__nome', 'raca__nome')

@admin.register(Gato)
class GatoAdmin(admin.ModelAdmin):
    list_display = ('animal', 'raca')
    list_filter = ('raca',)
    search_fields = ('animal__nome', 'raca__nome')

@admin.register(Adocao)
class AdocaoAdmin(admin.ModelAdmin):
    list_display = ('animal', 'adotante', 'data_requisicao')
    list_filter = ('data_requisicao',)
    search_fields = ('animal__nome', 'adotante__username')

@admin.register(Dose)
class DoseAdmin(admin.ModelAdmin):
    list_display = ('animal', 'vacina', 'data_aplicacao')
    list_filter = ('data_aplicacao', 'vacina')
    search_fields = ('animal__nome', 'vacina__nome')

@admin.register(Vacinas)
class VacinasAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ('logradouro', 'numero', 'bairro', 'cep')
    search_fields = ('logradouro', 'bairro', 'cep')

# Customize the User admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'telefone', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('telefone', 'profissao', 'estado_civil')}),
    )

admin.site.register(User, CustomUserAdmin)
