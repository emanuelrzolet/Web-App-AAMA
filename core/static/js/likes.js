function initializeLikeButtons() {
    document.querySelectorAll('.like-button').forEach(button => {
        const animalId = button.dataset.animalId;
        
        // Verifica se o usuário já deu like
        fetch(`/animal/${animalId}/is-liked/`)
            .then(response => response.json())
            .then(data => {
                const icon = button.querySelector('i');
                if (data.liked) {
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                } else {
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                }
                button.nextElementSibling.textContent = `${data.likes_count} likes`;
            })
            .catch(error => console.error('Erro ao verificar like:', error));

        // Adiciona o evento de click
        button.addEventListener('click', function() {
            fetch(`/animal/${animalId}/toggle-like/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => {
                if (response.status === 403) {
                    // Usuário não está logado
                    window.location.href = '/login/';
                    return;
                }
                return response.json();
            })
            .then(data => {
                if (data) {
                    const icon = button.querySelector('i');
                    if (data.liked) {
                        icon.classList.remove('far');
                        icon.classList.add('fas');
                    } else {
                        icon.classList.remove('fas');
                        icon.classList.add('far');
                    }
                    button.nextElementSibling.textContent = `${data.likes_count} likes`;
                }
            })
            .catch(error => console.error('Erro ao dar like:', error));
        });
    });
}

// Função para obter o cookie do CSRF token
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

// Inicializa os botões de like quando o documento carrega
document.addEventListener('DOMContentLoaded', initializeLikeButtons); 