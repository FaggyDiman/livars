function showModal(id) {
    document.getElementById(id).style.display = 'block';
}

function hideModal(id) {
    document.getElementById(id).style.display = 'none';
}

async function handleForm(event, url) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());

    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    const result = await response.json();
    if (result.status === 'ok') {
        location.reload();
    } else {
        alert(result.message || 'Произошла ошибка');
    }
}

document.getElementById('loginForm').onsubmit = (e) => handleForm(e, '/login');
document.getElementById('registerForm').onsubmit = (e) => handleForm(e, '/register');

async function logout() {
    const response = await fetch('/logout', { method: 'POST' });
    if (response.ok) location.reload();
}

// Закрытие модалок при клике вне их области
window.onclick = function(event) {
    if (event.target.className === 'modal') {
        event.target.style.display = 'none';
    }
}