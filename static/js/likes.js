function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function toggleLike(animalId, button) {
    fetch(`/animal/${animalId}/toggle-like/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        const likeIcon = button.querySelector('i');
        const likeCount = button.querySelector('.like-count');
        
        if (data.liked) {
            likeIcon.classList.remove('far');
            likeIcon.classList.add('fas');
        } else {
            likeIcon.classList.remove('fas');
            likeIcon.classList.add('far');
        }
        
        likeCount.textContent = data.likes_count;
    })
    .catch(error => console.error('Error:', error));
}

function checkLikeStatus(animalId, button) {
    fetch(`/animal/${animalId}/is-liked/`)
    .then(response => response.json())
    .then(data => {
        const likeIcon = button.querySelector('i');
        const likeCount = button.querySelector('.like-count');
        
        if (data.liked) {
            likeIcon.classList.remove('far');
            likeIcon.classList.add('fas');
        } else {
            likeIcon.classList.remove('fas');
            likeIcon.classList.add('far');
        }
        
        likeCount.textContent = data.likes_count;
    })
    .catch(error => console.error('Error:', error));
}

// Função para renderizar o card de animal na HOME (coração estático)
function renderAnimalCardStatic(animal) {
    return `
        <div class="animal-card">
            <div class="card-image">
                ${animal.foto_url ? `<img src="${animal.foto_url}" alt="${animal.nome}" class="img-fluid">` : `<img src="/static/images/no-photo.png" alt="Sem foto" class="img-fluid">`}
            </div>
            <div class="card-content">
                <div class="card-header">
                    <h3 class="animal-name">${animal.nome}</h3>
                    <span class="animal-type">${animal.tipo}</span>
                </div>
                <div class="likes-section">
                    <span class="like-icon-static">
                        <i class="${animal.likes_count >= 1 ? 'fas' : 'far'} fa-heart" style="color: ${animal.likes_count >= 1 ? 'red' : '#aaa'};"></i>
                    </span>
                    <span class="likes-count">${animal.likes_count} likes</span>
                </div>
                <p class="animal-description">${animal.descricao || ''}</p>
                <a href="/animal/${animal.id}/" class="conhecer-button">Conhecer ${animal.nome}</a>
            </div>
        </div>
    `;
}

// Exemplo: uso na HOME para montar o grid
// Supondo que você faz fetch('/api/animals/') e recebe data.animals
//
// document.getElementById('animal-grid').innerHTML = data.animals.map(renderAnimalCardStatic).join('');

// O código abaixo só ativa os likes clicáveis nas páginas de detalhe (onde existe .like-button)
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('animal-grid')) {
        // Renderiza cards estáticos na HOME
        fetch('/api/animals/')
        .then(response => response.json())
        .then(data => {
            document.getElementById('animal-grid').innerHTML = data.animals.map(renderAnimalCardStatic).join('');
        })
        .catch(error => console.error('Error:', error));
    } else {
        // Ativa likes clicáveis nas páginas de detalhe
        const likeButtons = document.querySelectorAll('.like-button');
        likeButtons.forEach(button => {
            const animalId = button.dataset.animalId;
            checkLikeStatus(animalId, button);
            button.addEventListener('click', function(e) {
                e.preventDefault();
                toggleLike(animalId, button);
            });
        });
    }
});