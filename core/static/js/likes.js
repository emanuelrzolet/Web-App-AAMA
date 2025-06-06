document.addEventListener('DOMContentLoaded', function () {
    // Função para obter o token CSRF dos cookies
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
    const csrftoken = getCookie('csrftoken');

    // Delegação de evento para os botões de like
    // Escuta cliques no #animal-grid, mas só age se o clique foi em .like-button
    const animalGrid = document.getElementById('animal-grid');

    // Suporte ao botão de like na página de detalhes do animal
    const detailLikeButton = document.querySelector('.like-button[data-animal-id]');
    if (detailLikeButton) {
        detailLikeButton.addEventListener('click', function (event) {
            event.preventDefault();
            console.log('Like button (detalhe) clicado!');
            const animalId = detailLikeButton.dataset.animalId;
            console.log('Enviando fetch para toggle-like:', animalId);
            fetch(`/animal/${animalId}/toggle-like/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                },
            })
            .then(response => {
                console.log('Status da resposta:', response.status);
                if (response.status === 401 || response.status === 403) {
                    return response.json().then(data => {
                        console.log('Dados recebidos para login:', data);
                        if (data.login_url) {
                            console.log('Redirecionando para:', data.login_url);
                            window.location.href = data.login_url;
                        } else {
                            alert('Você precisa estar logado para curtir. Redirecionando para login.');
                            window.location.href = '/accounts/login/';
                        }
                        return Promise.reject('Redirecting to login');
                    }).catch((e) => {
                        console.log('Erro ao fazer parse do JSON:', e);
                        alert('Você precisa estar logado para curtir. Redirecionando para login.');
                        window.location.href = '/accounts/login/';
                        return Promise.reject('Redirecting to login');
                    });
                }
                if (!response.ok) {
                    throw new Error('Falha ao curtir o animal. Status: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                // Atualize o ícone e contagem se desejar
                if (data.liked !== undefined) {
                    const heartIcon = detailLikeButton.querySelector('i');
                    const likesCountSpan = detailLikeButton.querySelector('.like-count');

                    if (data.liked) {
                        heartIcon.classList.remove('far');
                        heartIcon.classList.add('fas', 'liked-heart');
                    } else {
                        heartIcon.classList.remove('fas', 'liked-heart');
                        heartIcon.classList.add('far');
                    }
                    if (likesCountSpan) {
                        likesCountSpan.textContent = data.likes_count || 0;
                    }
                }
            })
            .catch(error => {
                if (error !== 'Redirecting to login') {
                    console.error('Erro ao tentar curtir:', error);
                }
            })
            .catch(error => {
                console.error('Erro global no fetch do like:', error);
            });
        });
    }

    if (animalGrid) {
        animalGrid.addEventListener('click', function (event) {
            const likeButton = event.target.closest('.like-button');

            if (!likeButton) {
                return; // O clique não foi em um like-button ou seus filhos
            }

            const animalId = likeButton.dataset.animalId;
            if (!animalId) {
                console.error('Animal ID não encontrado no botão de like.');
                return;
            }

            fetch(`/animal/${animalId}/toggle-like/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                },
                // O corpo pode ser vazio se a view não esperar nada, 
                // ou você pode enviar algo se necessário.
                // body: JSON.stringify({}) 
            })
            .then(response => {
                if (response.status === 401 || response.status === 403) { // Não autenticado ou não autorizado
                    // Tenta extrair a URL de login da resposta, se existir
                    return response.json().then(data => {
                        if (data.login_url) {
                            window.location.href = data.login_url;
                        } else {
                            // Fallback se login_url não estiver presente
                            alert('Você precisa estar logado para curtir. Redirecionando para login.');
                            window.location.href = '/accounts/login/'; // Ou sua URL de login padrão
                        }
                        return Promise.reject('Redirecting to login'); // Previne processamento adicional
                    }).catch(() => {
                        // Fallback se a resposta não for JSON ou não tiver login_url
                        alert('Você precisa estar logado para curtir. Redirecionando para login.');
                        window.location.href = '/accounts/login/'; // Ou sua URL de login padrão
                        return Promise.reject('Redirecting to login');
                    });
                }
                if (!response.ok) {
                    throw new Error('Falha ao curtir o animal. Status: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                if (data.liked !== undefined) {
                    const heartIcon = likeButton.querySelector('i');
                    const likesCountSpan = likeButton.nextElementSibling; // Assume que o span de contagem é o próximo irmão

                    if (data.liked) {
                        heartIcon.classList.remove('far'); // Remove ícone de coração vazio
                        heartIcon.classList.add('fas', 'liked-heart'); // Adiciona ícone de coração cheio e classe 'liked-heart'
                    } else {
                        heartIcon.classList.remove('fas', 'liked-heart'); // Remove ícone de coração cheio e classe 'liked-heart'
                        heartIcon.classList.add('far'); // Adiciona ícone de coração vazio
                    }
                    
                    if (likesCountSpan && likesCountSpan.classList.contains('likes-count')) {
                        likesCountSpan.textContent = `${data.likes_count || 0} likes`;
                    } else {
                        // Se a estrutura for diferente, ajuste o seletor para o contador de likes
                        // Por exemplo, se o span estiver dentro do botão:
                        // const likesCountSpanInside = likeButton.querySelector('.likes-count-value');
                        // if (likesCountSpanInside) likesCountSpanInside.textContent = data.likes_count || 0;
                        console.warn('Span de contagem de likes não encontrado ou estrutura inesperada.');
                    }
                }
            })
            .catch(error => {
                if (error !== 'Redirecting to login') { // Não mostra erro se já está redirecionando
                    console.error('Erro ao tentar curtir:', error);
                    // alert('Ocorreu um erro ao tentar curtir. Tente novamente.');
                }
            });
        });
    } else {
        console.warn('#animal-grid não encontrado no DOM. A funcionalidade de like pode não funcionar.');
    }

    // Não precisamos mais de uma função initializeLikeButtons separada
    // A delegação de eventos cuida de todos os botões, mesmo os adicionados dinamicamente.
});