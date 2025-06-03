from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .models import Animal, RacaCachorro, RacaGato, Like
from django.views.decorators.csrf import csrf_protect

def home(request):
    return render(request, 'core/home.html')

def about(request):
    return render(request, 'about/index.html')

def donate(request):
    return render(request, 'donate/index.html')

def animal_list(request):
    return render(request, 'core/animal_list.html')

def animal_detail(request, pk):
    animal = get_object_or_404(Animal, pk=pk)
    fotos = animal.fotos_set.all()
    foto_principal = animal.foto_principal.url if getattr(animal, 'foto_principal', None) else None
    outras_fotos = [f for f in fotos if not f.is_principal]
    return render(request, 'core/animal_detail.html', {
        'animal': animal,
        'outras_fotos': outras_fotos,
        'foto_principal': foto_principal,
    })

def load_animals(request):
    page_number = request.GET.get('page', 1)
    filters = {}
    
    # Aplicando filtros
    tipo = request.GET.getlist('tipo[]')
    if tipo:
        if len(tipo) == 1:
            filters['tipo'] = tipo[0]
        else:
            filters['tipo__in'] = tipo
        
    idade = request.GET.get('idade')
    if idade:
        if idade == 'filhote':
            filters['idadeEstimada__lte'] = 2
        elif idade == 'adulto':
            filters['idadeEstimada__gt'] = 2
            filters['idadeEstimada__lte'] = 8
        elif idade == 'idoso':
            filters['idadeEstimada__gt'] = 8
            
    porte = request.GET.get('porte')
    if porte and ('CACHORRO' in tipo if tipo else False):
        filters['cachorro__porte'] = porte
        
    cor = request.GET.get('cor')
    if cor:
        filters['cor'] = cor

    pelagem = request.GET.get('pelagem')
    if pelagem:
        filters['pelagem'] = pelagem
        
    genero = request.GET.get('genero')
    if genero:
        filters['genero'] = genero

    castrado = request.GET.get('castrado')
    if castrado:
        filters['castrado'] = castrado.lower() == 'true'

    raca_cachorro = request.GET.get('raca_cachorro')
    if raca_cachorro and ('CACHORRO' in tipo if tipo else False):
        filters['cachorro__raca_id'] = raca_cachorro

    raca_gato = request.GET.get('raca_gato')
    if raca_gato and ('GATO' in tipo if tipo else False):
        filters['gato__raca_id'] = raca_gato

    # Filtrando apenas animais disponíveis para adoção
    filters['status'] = 'DISPONIVEL'
    
    animals = Animal.objects.filter(**filters).order_by('-entrada_instituicao')
    paginator = Paginator(animals, 9)  # 9 animais por página
    page = paginator.get_page(page_number)
    
    data = {
        'has_next': page.has_next(),
        'animals': [
            {
                'id': animal.id,
                'nome': animal.nome,
                'tipo': animal.get_tipo_display(),
                'idade_aproximada': animal.idadeEstimada * 12 if animal.idadeEstimada else 0,
                'foto_url': animal.foto_principal.url if animal.foto_principal else None,
                'descricao': animal.descricao or '',
                'genero': animal.get_genero_display(),
                'pelagem': animal.get_pelagem_display(),
                'porte': animal.cachorro.get_porte_display() if hasattr(animal, 'cachorro') else None,
                'cor': animal.get_cor_display(),
                'raca': animal.cachorro.raca.nome if hasattr(animal, 'cachorro') else (animal.gato.raca.nome if hasattr(animal, 'gato') else None),
                'likes_count': animal.likes_count,
            }
            for animal in page.object_list
        ]
    }
    
    return JsonResponse(data)

@require_POST
@login_required
def create_adocao(request):
    try:
        data = json.loads(request.body)
        animal_id = data.get('animal_id')
        
        animal = get_object_or_404(Animal, id=animal_id, pertence_instituicao=True)
        
        # Verifica se já existe uma adoção pendente para este animal
        if Adocao.objects.filter(animal=animal, status='pendente').exists():
            return JsonResponse({'success': False, 'error': 'Este animal já possui uma solicitação de adoção pendente.'})
        
        # Cria a solicitação de adoção
        Adocao.objects.create(
            animal=animal,
            adotante=request.user
        )
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_protect
def add_raca_cachorro(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        if nome:
            try:
                # Tenta encontrar uma raça existente primeiro
                raca = RacaCachorro.objects.filter(nome__iexact=nome).first()
                if not raca:
                    # Se não existir, cria uma nova
                    raca = RacaCachorro.objects.create(nome=nome)
                return JsonResponse({
                    'success': True,
                    'id': raca.id,
                    'nome': raca.nome
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=400)
    return JsonResponse({
        'success': False,
        'error': 'Requisição inválida'
    }, status=400)

def get_cores(request):
    # Retorna apenas cores que estão associadas a pelo menos um animal disponível
    cores = Animal.objects.filter(status='DISPONIVEL').values_list('cor', flat=True).distinct()
    # Remove valores vazios e normaliza para maiúsculas
    cores = [c.upper() for c in cores if c]
    # Filtra apenas cores válidas
    cor_validas = set([c[0] for c in Animal.COR_CHOICES])
    cores = [c for c in cores if c in cor_validas]
    choices_dict = dict(Animal.COR_CHOICES)
    cores_list = [{'value': c, 'label': choices_dict.get(c, c)} for c in cores]
    return JsonResponse({'cores': cores_list})

@csrf_protect
def add_raca_gato(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        if nome:
            try:
                # Tenta encontrar uma raça existente primeiro
                raca = RacaGato.objects.filter(nome__iexact=nome).first()
                if not raca:
                    # Se não existir, cria uma nova
                    raca = RacaGato.objects.create(nome=nome)
                return JsonResponse({
                    'success': True,
                    'id': raca.id,
                    'nome': raca.nome
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=400)
    return JsonResponse({
        'success': False,
        'error': 'Requisição inválida'
    }, status=400)

@login_required
def toggle_like(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id)
    like, created = Like.objects.get_or_create(user=request.user, animal=animal)
    
    if not created:
        # If the like already existed, remove it (unlike)
        like.delete()
        liked = False
    else:
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'likes_count': animal.likes_count
    })

def is_animal_liked(request, animal_id):
    if not request.user.is_authenticated:
        return JsonResponse({'liked': False})
    
    animal = get_object_or_404(Animal, id=animal_id)
    liked = Like.objects.filter(user=request.user, animal=animal).exists()
    
    return JsonResponse({
        'liked': liked,
        'likes_count': animal.likes_count
    })

from django.db.models import Exists, OuterRef

def get_racas(request):
    tipo = request.GET.get('tipo')
    if tipo == 'CACHORRO':
        racas = RacaCachorro.objects.annotate(
            tem_disponivel=Exists(
                Animal.objects.filter(
                    tipo='CACHORRO',
                    status='DISPONIVEL',
                    cachorro__raca=OuterRef('pk')
                )
            )
        ).filter(tem_disponivel=True).values('id', 'nome')
    elif tipo == 'GATO':
        racas = RacaGato.objects.annotate(
            tem_disponivel=Exists(
                Animal.objects.filter(
                    tipo='GATO',
                    status='DISPONIVEL',
                    gato__raca=OuterRef('pk')
                )
            )
        ).filter(tem_disponivel=True).values('id', 'nome')
    else:
        racas = []
    
    return JsonResponse({'racas': list(racas)})
