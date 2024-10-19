// Authentication related JavaScript

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.querySelector('#login-form');
    const registerForm = document.querySelector('#register-form');

    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
});

async function handleLogin(event) {
    event.preventDefault();
    const username = document.querySelector('#username').value;
    const password = document.querySelector('#password').value;

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'username': username,
                'password': password,
            }),
        });

        if (response.ok) {
            window.location.href = '/dashboard';
        } else {
            const data = await response.json();
            showNotification(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showNotification('An error occurred during login', 'error');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const username = document.querySelector('#username').value;
    const email = document.querySelector('#email').value;
    const password = document.querySelector('#password').value;

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'username': username,
                'email': email,
                'password': password,
            }),
        });

        if (response.ok) {
            showNotification('Registration successful. Please log in.');
            window.location.href = '/login';
        } else {
            const data = await response.json();
            showNotification(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showNotification('An error occurred during registration', 'error');
    }
}
