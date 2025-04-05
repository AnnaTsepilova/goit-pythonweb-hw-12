import datetime

def test_create_contact(client, get_token):
    """Test create contact endpoint

    Args:
        client (_type_): HTTP client
        get_token (_type_): JWT token
    """
    response = client.post(
        "/api/contacts",
        json={
            "firstname": "sdfsdfsdfwef",
            "lastname": "sdfsdfsdf",
            "email": "ffffffff@email.com",
            "phone": "380671222222",
            "birthday": "1980-01-01",
            "description": "Lorem ipsum description",
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["firstname"] == "sdfsdfsdfwef"
    assert data["lastname"] == "sdfsdfsdf"
    assert data["email"] == "ffffffff@email.com"
    assert data["phone"] == "380671222222"
    assert data["birthday"] == "1980-01-01"
    assert data["description"] == "Lorem ipsum description"
    assert "id" in data


def test_get_contact(client, get_token):
    """Test get contact endpoint

    Args:
        client (_type_): HTTP client
        get_token (_type_): JWT token
    """
    response = client.get(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["firstname"] == "sdfsdfsdfwef"
    assert data["lastname"] == "sdfsdfsdf"
    assert data["email"] == "ffffffff@email.com"
    assert data["phone"] == "380671222222"
    assert data["birthday"] == "1980-01-01"
    assert data["description"] == "Lorem ipsum description"
    assert "id" in data


def test_get_contact_not_found(client, get_token):
    response = client.get(
        "/api/contacts/2", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_get_contacts(client, get_token):
    response = client.get(
        "/api/contacts", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["firstname"] == "sdfsdfsdfwef"
    assert data[0]["lastname"] == "sdfsdfsdf"
    assert data[0]["email"] == "ffffffff@email.com"
    assert data[0]["phone"] == "380671222222"
    assert data[0]["birthday"] == "1980-01-01"
    assert data[0]["description"] == "Lorem ipsum description"
    assert "id" in data[0]

def test_update_incorrect_data(client, get_token):
    response = client.put(
        "/api/contacts/1",
        json={"somedata": "NewContactName", "done": 1},
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 422, response.text

def test_update_contact(client, get_token):
    date_test = datetime.datetime.now() + datetime.timedelta(days=5)
    date_time = date_test.strftime("%Y-%m-%d")
    response = client.put(
        "/api/contacts/1",
        json={
            "firstname": "NewContactName",
            "lastname": "NewContactlLstname",
            "email": "newemail@email.com",
            "phone": "380671333333",
            "birthday": date_time,
            "description": "Lorem ipsum description",
            "done": 0,
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["firstname"] == "NewContactName"
    assert data["lastname"] == "NewContactlLstname"
    assert data["email"] == "newemail@email.com"
    assert data["phone"] == "380671333333"
    assert data["birthday"] == date_time
    assert data["description"] == "Lorem ipsum description"
    assert "id" in data

def test_update_contact_status(client, get_token):
    date_test = datetime.datetime.now() + datetime.timedelta(days=5)
    date_time = date_test.strftime("%Y-%m-%d")
    response = client.patch(
        "/api/contacts/1",
        json={
            "done": 1,
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["firstname"] == "NewContactName"
    assert data["lastname"] == "NewContactlLstname"
    assert data["email"] == "newemail@email.com"
    assert data["phone"] == "380671333333"
    assert data["birthday"] == date_time
    assert data["description"] == "Lorem ipsum description"
    assert "id" in data

def test_update_contact_status_notfound(client, get_token):
    response = client.patch(
        "/api/contacts/3",
        json={
            "done": 1,
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"

def test_get_contacts_birthdays(client, get_token):
    date_test = datetime.datetime.now() + datetime.timedelta(days=5)
    date_time = date_test.strftime("%Y-%m-%d")
    response = client.get(
        "/api/contacts/birthdays/", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    print(data)
    assert isinstance(data, list)
    assert data[0]["firstname"] == "NewContactName"
    assert data[0]["lastname"] == "NewContactlLstname"
    assert data[0]["email"] == "newemail@email.com"
    assert data[0]["phone"] == "380671333333"
    assert data[0]["birthday"] == date_time
    assert data[0]["description"] == "Lorem ipsum description"
    assert "id" in data[0]

def test_search_contact(client, get_token):
    response = client.get(
        "/api/contacts/search/email?query=newemail@email.com",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data[0]["firstname"] == "NewContactName"
    assert data[0]["lastname"] == "NewContactlLstname"
    assert data[0]["email"] == "newemail@email.com"
    assert data[0]["phone"] == "380671333333"
    assert data[0]["description"] == "Lorem ipsum description"
    assert "id" in data[0]

def test_update_contact_not_found(client, get_token):
    response = client.put(
        "/api/contacts/2",
        json={
            "firstname": "NewContactName",
            "lastname": "NewContactlLstname",
            "email": "newemail@email.com",
            "phone": "380671333333",
            "birthday": "1980-02-10",
            "description": "Lorem ipsum description",
            "done": 1,
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["firstname"] == "NewContactName"
    assert "id" in data


def test_repeat_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"
