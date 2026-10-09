/**
 * GRAND ROYAL HOTEL - Automatic CSRF Protection
 * Transparently attaches X-CSRFToken header to all state-altering fetch requests (POST, PUT, DELETE, PATCH).
 */
(function () {
    'use strict';

    /**
     * Retrieve CSRF token from HTML meta tag or hidden input field
     */
    function getCsrfToken() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag && metaTag.getAttribute('content')) {
            return metaTag.getAttribute('content');
        }
        const inputTag = document.querySelector('input[name="csrf_token"]');
        if (inputTag && inputTag.value) {
            return inputTag.value;
        }
        return '';
    }

    // Expose utility globally
    window.getCsrfToken = getCsrfToken;

    // Intercept native window.fetch to automatically include CSRF token for mutating methods
    const originalFetch = window.fetch;
    window.fetch = function (resource, init = {}) {
        const method = (init.method || 'GET').toUpperCase();
        const mutatingMethods = ['POST', 'PUT', 'DELETE', 'PATCH'];

        if (mutatingMethods.includes(method)) {
            const token = getCsrfToken();
            if (token) {
                if (!init.headers) {
                    init.headers = {};
                }

                if (init.headers instanceof Headers) {
                    if (!init.headers.has('X-CSRFToken')) {
                        init.headers.set('X-CSRFToken', token);
                    }
                } else if (Array.isArray(init.headers)) {
                    const hasToken = init.headers.some(([k]) => k.toLowerCase() === 'x-csrftoken');
                    if (!hasToken) {
                        init.headers.push(['X-CSRFToken', token]);
                    }
                } else {
                    if (!init.headers['X-CSRFToken'] && !init.headers['x-csrftoken']) {
                        init.headers['X-CSRFToken'] = token;
                    }
                }
            }
        }

        return originalFetch.call(this, resource, init);
    };

    // Attach token to any standard HTML forms dynamically on DOM load if not present
    document.addEventListener('DOMContentLoaded', () => {
        const token = getCsrfToken();
        if (!token) return;

        document.querySelectorAll('form[method="POST"], form[method="post"]').forEach(form => {
            if (!form.querySelector('input[name="csrf_token"]')) {
                const hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.name = 'csrf_token';
                hiddenInput.value = token;
                form.prepend(hiddenInput);
            }
        });
    });
})();
