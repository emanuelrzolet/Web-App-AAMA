from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .models import Animal, Adocao
from .forms import UserRegistrationForm

def home(request):
    return render(request, 'core/home.html')

def animal_list(request):
    return render(request, 'core/animal_list.html')

def animal_detail(request, pk):
    animal = get_object_or_404(Animal, pk=pk)
    return render(request, 'core/animal_detail.html', {'animal': animal})

def load_animals(request):
    page_number = request.GET.get('page', 1)
    filters = {}
    
    # Aplicando filtros
    especie = request.GET.get('especie')
    if especie:
        filters['especie'] = especie
        
    idade = request.GET.get('idade')
    if idade:
        if idade == 'filhote':
            filters['idadeEstimada__lte'] = 12
        elif idade == 'adulto':
            filters['idadeEstimada__gt'] = 12
            filters['idadeEstimada__lte'] = 84
        elif idade == 'idoso':
            filters['idadeEstimada__gt'] = 84
            
    porte = request.GET.get('porte')
    if porte and hasattr(Animal, 'porte'):
        filters['porte'] = porte
        
    sexo = request.GET.get('sexo')
    if sexo:
        filters['genero'] = sexo

    # Filtrando apenas animais disponíveis para adoção
    filters['pertence_instituicao'] = True
    
    animals = Animal.objects.filter(**filters).order_by('-entrada_instituicao')
    paginator = Paginator(animals, 9)  # 9 animais por página
    page = paginator.get_page(page_number)
    
    data = {
        'has_next': page.has_next(),
        'animals': [
            {
                'id': animal.id,
                'nome': animal.nome,
                'especie': 'Cachorro' if hasattr(animal, 'cachorro') else 'Gato',
                'idade_aproximada': animal.idadeEstimada * 12 if animal.idadeEstimada else 0,
                'foto_url': animal.foto_principal.url if animal.foto_principal else None,
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

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registro realizado com sucesso!')
            return redirect('home')
        else:
            messages.error(request, 'Erro ao registrar. Por favor, corrija os erros abaixo.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'core/registration/register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'core/profile.html')
