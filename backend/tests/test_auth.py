def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "fullName": "Test User",
            "birthPlace": "Jakarta",
            "birthDate": "1995-04-03",
            "nik": "3171020304950001",
            "noKtp": "3171020304950001",
            "gender": "Laki-laki",
            "education": "S1",
            "church_domisili": "GKI Harapan Indah",
            "church_central": "GKI",
            "married": "Menikah",
            "chatecication": "Sudah",
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword123",
            "confirmPassword": "testpassword123",
            "phone": "081234567890",
            "origin": "Jakarta",
            "address": "Jl. Test No. 1",
            "photoUrl": None
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data

def test_login_user(client):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_user_by_username_and_nik(client):
    for identifier in ("testuser", "3171020304950001"):
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": identifier,
                "password": "testpassword123"
            }
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

def test_login_user_normalizes_email_identifier(client):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": " TESTUSER@EXAMPLE.COM ",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
