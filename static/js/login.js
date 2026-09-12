/**
 * GRAND ROYAL HOTEL - Restaurant Login Logic
 */
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const passwordInput = document.getElementById('password');
    const togglePasswordBtn = document.getElementById('togglePassword');
    const alertBox = document.getElementById('loginAlert');

    // Toggle show / hide password
    if (togglePasswordBtn && passwordInput) {
        togglePasswordBtn.addEventListener('click', () => {
            const isPassword = passwordInput.type === 'password';
            passwordInput.type = isPassword ? 'text' : 'password';
            const icon = togglePasswordBtn.querySelector('i');
            if (icon) {
                icon.className = isPassword ? 'bi bi-eye-slash' : 'bi bi-eye';
            }
        });
    }

    // Quick demo credential autofill
    window.fillCredentials = function(username, password) {
        const uField = document.getElementById('username');
        const pField = document.getElementById('password');
        if (uField && pField) {
            uField.value = username;
            pField.value = password;
            uField.focus();
        }
    };

    // AJAX login submission
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();
            const rememberMe = document.getElementById('rememberMe')?.checked || false;

            if (!username || !password) {
                showAlert('Please enter both username and password.', 'danger');
                return;
            }

            const submitBtn = loginForm.querySelector('button[type="submit"]');
            const origText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Authenticating...';

            try {
                const res = await fetch('/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password, remember_me: rememberMe })
                });

                const result = await res.json();

                if (res.ok && result.success) {
                    showAlert(result.message || 'Login successful! Redirecting...', 'success');
                    setTimeout(() => {
                        window.location.href = result.redirect || '/';
                    }, 600);
                } else {
                    showAlert(result.error || 'Invalid credentials. Please try again.', 'danger');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = origText;
                }
            } catch (err) {
                showAlert('Server connection error. Please ensure Flask backend is running.', 'danger');
                submitBtn.disabled = false;
                submitBtn.innerHTML = origText;
            }
        });
    }

    function showAlert(msg, type) {
        if (!alertBox) return;
        alertBox.className = `alert alert-${type} py-2 px-3 mb-3 d-flex align-items-center`;
        alertBox.innerHTML = `<i class="bi ${type === 'success' ? 'bi-check-circle' : 'bi-exclamation-triangle'} me-2"></i> ${msg}`;
        alertBox.classList.remove('d-none');
    }
});
