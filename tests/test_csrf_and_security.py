import re
import pytest
from flask import session


def test_csrf_token_required_on_post_when_enabled(csrf_client):
    """When CSRF is enabled, mutating requests without a CSRF token must be rejected with 400."""
    res = csrf_client.post('/login', json={
        'username': 'admin_csrf',
        'password': 'AdminPass123!'
    })
    # Must fail with 400 Bad Request due to missing CSRF token
    assert res.status_code == 400
    data = res.get_json()
    assert data['success'] is False
    assert 'CSRF' in data['error']


def test_csrf_token_accepted_when_valid(csrf_client):
    """When a valid CSRF token is provided in the X-CSRFToken header, the request succeeds."""
    # 1. Access the login GET page to generate a session and retrieve the rendered CSRF token
    get_res = csrf_client.get('/login')
    assert get_res.status_code == 200
    html = get_res.get_data(as_text=True)

    # Extract token from meta tag: <meta name="csrf-token" content="...">
    token_match = re.search(r'<meta name="csrf-token" content="([^"]+)">', html)
    assert token_match is not None, "CSRF token meta tag not found in login page HTML"
    csrf_token = token_match.group(1)

    # 2. Submit POST with valid X-CSRFToken header
    post_res = csrf_client.post(
        '/login',
        json={'username': 'admin_csrf', 'password': 'AdminPass123!'},
        headers={'X-CSRFToken': csrf_token}
    )
    assert post_res.status_code == 200
    data = post_res.get_json()
    assert data['success'] is True
    assert data['user']['username'] == 'admin_csrf'


def test_login_invalid_credentials_returns_401(client):
    """Attempting login with incorrect password returns 401."""
    res = client.post('/login', json={
        'username': 'admin_tester',
        'password': 'WrongPassword123'
    })
    assert res.status_code == 401
    data = res.get_json()
    assert data['success'] is False
    assert 'Invalid username or password' in data['error']


def test_login_missing_fields_returns_400(client):
    """Missing username or password returns 400."""
    res = client.post('/login', json={'username': 'admin_tester'})
    assert res.status_code == 400
    data = res.get_json()
    assert data['success'] is False


def test_session_security_settings(app):
    """Enforce session security flags: HttpOnly and SameSite."""
    assert app.config['SESSION_COOKIE_HTTPONLY'] is True
    assert app.config['SESSION_COOKIE_SAMESITE'] in ('Lax', 'Strict')
