document.getElementById('loginForm')?.addEventListener('submit', function (e) {
    e.preventDefault();
    const nickname = document.getElementById('login-nickname').value;
    const password = document.getElementById('login-password').value;
    const messageDiv = document.getElementById('login-message');
    fetch('/api/authorization/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nickname, password })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                messageDiv.textContent = 'Redirecting...';
                window.location.href = data.data.preferred_redirect || '/';
            } else {
                messageDiv.textContent = 'Error: ' + data.error.message;
            }
        })
        .catch(error => {
            messageDiv.textContent = 'Connection error';
        });
});

document.getElementById('registerForm')?.addEventListener('submit', function (e) {
    e.preventDefault();
    const nickname = document.getElementById('reg-nickname').value;
    const password = document.getElementById('reg-password').value;
    const messageDiv = document.getElementById('register-message');
    fetch('/api/authorization/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nickname, password })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                messageDiv.textContent = 'Success! Redirecting...';
                window.location.href = data.data.preferred_redirect || '/';
            } else {
                if (data.error.details && Array.isArray(data.error.details)) {
                    messageDiv.textContent = data.error.details.join('; ');
                } else {
                    messageDiv.textContent = 'Error: ' + data.error.message;
                }
            }
        })
        .catch(error => {
            messageDiv.textContent = 'Connection error';
        });
});
