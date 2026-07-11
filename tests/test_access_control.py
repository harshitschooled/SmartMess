import pytest

def test_student_access_control(client, seed_users):
    # Log in as Student
    client.post('/auth/login', data={'email': 'student@test.com', 'password': 'student123'})
    
    # Can access student dashboard
    response = client.get('/student/dashboard')
    assert response.status_code == 200
    
    # Cannot access admin dashboard
    response = client.get('/admin/dashboard')
    assert response.status_code == 403
    
    # Cannot access menu management
    response = client.get('/admin/menus')
    assert response.status_code == 403

def test_admin_access_control(client, seed_users):
    # Log in as Admin
    client.post('/auth/login', data={'email': 'admin@test.com', 'password': 'admin123'})
    
    # Can access admin dashboard
    response = client.get('/admin/dashboard')
    assert response.status_code == 200
    
    # Cannot access student dashboard
    response = client.get('/student/dashboard')
    assert response.status_code == 403
