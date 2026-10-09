/**
 * GRAND ROYAL HOTEL - Staff & Admin Registration Logic
 * Real-time password strength validation, confirm match, and AJAX registration
 */
document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('registerForm');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const togglePasswordBtn = document.getElementById('togglePassword');
    const toggleConfirmBtn = document.getElementById('toggleConfirmPassword');
    const alertBox = document.getElementById('registerAlert');
    const strengthFill = document.getElementById('strengthFill');
    const strengthText = document.getElementById('strengthText');
    const matchFeedback = document.getElementById('passwordMatchFeedback');

    // Toggle password visibility
    if (togglePasswordBtn && passwordInput) {
        togglePasswordBtn.addEventListener('click', () => {
            const isPass = passwordInput.type === 'password';
            passwordInput.type = isPass ? 'text' : 'password';
            const icon = togglePasswordBtn.querySelector('i');
            if (icon) icon.className = isPass ? 'bi bi-eye-slash' : 'bi bi-eye';
        });
    }

    // Toggle confirm password visibility
    if (toggleConfirmBtn && confirmPasswordInput) {
        toggleConfirmBtn.addEventListener('click', () => {
            const isPass = confirmPasswordInput.type === 'password';
            confirmPasswordInput.type = isPass ? 'text' : 'password';
            const icon = toggleConfirmBtn.querySelector('i');
            if (icon) icon.className = isPass ? 'bi bi-eye-slash' : 'bi bi-eye';
        });
    }

    // Password strength evaluator
    if (passwordInput && strengthFill && strengthText) {
        passwordInput.addEventListener('input', () => {
            const val = passwordInput.value;
            let score = 0;

            if (val.length >= 6) score++;
            if (val.length >= 8) score++;
            if (/[0-9]/.test(val)) score++;
            if (/[A-Z]/.test(val) && /[a-z]/.test(val)) score++;
            if (/[^A-Za-z0-9]/.test(val)) score++;

            strengthFill.className = 'password-strength-fill';
            if (val.length === 0) {
                strengthFill.style.width = '0%';
                strengthText.textContent = '';
            } else if (score <= 2) {
                strengthFill.classList.add('strength-weak');
                strengthText.textContent = 'Weak password (min 6 characters required)';
                strengthText.className = 'text-danger small mt-1';
            } else if (score <= 4) {
                strengthFill.classList.add('strength-medium');
                strengthText.textContent = 'Moderate password strength';
                strengthText.className = 'text-warning small mt-1';
            } else {
                strengthFill.classList.add('strength-strong');
                strengthText.textContent = 'Strong & secure password';
                strengthText.className = 'text-success small mt-1';
            }

            checkPasswordMatch();
        });
    }

    // Confirm password match checker
    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', checkPasswordMatch);
    }

    function checkPasswordMatch() {
        if (!confirmPasswordInput || !passwordInput || !matchFeedback) return;
        const p1 = passwordInput.value;
        const p2 = confirmPasswordInput.value;

        if (!p2) {
            matchFeedback.textContent = '';
            matchFeedback.className = 'small';
            return;
        }

        if (p1 === p2) {
            matchFeedback.textContent = '✓ Passwords match';
            matchFeedback.className = 'text-success small fw-semibold mt-1';
        } else {
            matchFeedback.textContent = '✗ Passwords do not match';
            matchFeedback.className = 'text-danger small fw-semibold mt-1';
        }
    }

    // AJAX Form submission
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const fullName = document.getElementById('full_name').value.trim();
            const username = document.getElementById('username').value.trim();
            const email = document.getElementById('email')?.value.trim() || '';
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password')?.value;
            const role = document.getElementById('role')?.value || 'staff';

            // Validate fields
            if (!fullName || !username || !password) {
                showAlert('Please fill in all required fields.', 'danger');
                return;
            }

            if (username.length < 3) {
                showAlert('Username must be at least 3 characters long.', 'danger');
                return;
            }

            if (password.length < 6) {
                showAlert('Password must be at least 6 characters long.', 'danger');
                return;
            }

            if (confirmPassword !== undefined && password !== confirmPassword) {
                showAlert('Passwords do not match. Please verify.', 'danger');
                return;
            }

            const submitBtn = registerForm.querySelector('button[type="submit"]');
            const origHtml = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Creating Account...';

            try {
                const res = await fetch('/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        full_name: fullName,
                        username: username,
                        email: email,
                        password: password,
                        role: role
                    })
                });

                const data = await res.json();

                if (res.ok && data.success) {
                    showAlert(data.message || 'Account registered successfully! Redirecting to login...', 'success');
                    setTimeout(() => {
                        window.location.href = data.redirect || '/login';
                    }, 1200);
                } else {
                    showAlert(data.error || 'Failed to create account.', 'danger');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = origHtml;
                }
            } catch (err) {
                showAlert('Server connection error. Please try again.', 'danger');
                submitBtn.disabled = false;
                submitBtn.innerHTML = origHtml;
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
