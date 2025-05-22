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

// Initialize like buttons when the page loads
document.addEventListener('DOMContentLoaded', function() {
    const likeButtons = document.querySelectorAll('.like-button');
    likeButtons.forEach(button => {
        const animalId = button.dataset.animalId;
        checkLikeStatus(animalId, button);
        
        button.addEventListener('click', function(e) {
            e.preventDefault();
            toggleLike(animalId, button);
        });
    });
}); 