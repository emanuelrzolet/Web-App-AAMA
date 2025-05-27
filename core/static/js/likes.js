function initializeLikeButtons() {
    document.querySelectorAll('.like-button').forEach(button => {
        const animalId = button.dataset.animalId;

        // 1. Verifica se o usuário já deu like (Requisição GET)
        fetch(`/animal/${animalId}/is-liked/`) // <-- Esta é a requisição GET
            .then(response => response.json())
            .then(data => {
                // ... Atualiza o ícone e a contagem de likes ...
                button.nextElementSibling.textContent = `${data.likes_count} likes`;
            })
            .catch(error => console.error('Erro ao verificar like:', error));

        // 2. Adiciona o evento de click (Requisição POST)
        button.addEventListener('click', function() {
            fetch(`/animal/${animalId}/toggle-like/`, { // <-- Esta é a requisição POST
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => {
                if (response.status === 403) {
                    // Usuário não está logado
                    window.location.href = '/login/'; // <-- ESTE É O REDIRECIONAMENTO PARA LOGIN!
                    return;
                }
                return response.json();
            })
            .then(data => {
                // ... Atualiza o ícone e a contagem de likes após o toggle ...
            })
            .catch(error => console.error('Erro ao dar like:', error));
        });
    });
}