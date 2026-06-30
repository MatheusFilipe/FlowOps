from http import HTTPStatus


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'name': 'teste',
            'phone': '+551140028922',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'name': 'teste',
        'phone': 'tel:+55-11-4002-8922',
        'address': None,
    }


def test_create_user_conflict(client, user):
    response = client.post(
        '/users/',
        json={
            'name': 'teste',
            'phone': '+551140028922',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Usuário já cadastrado.'}


def test_list_users(client, user):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'id': 1,
                'name': 'user',
                'phone': 'tel:+55-11-4002-8922',
                'address': 'Rua dos Bobos, n° 0',
            }
        ]
    }


def test_list_users_empty(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_update_user(client, user):
    response = client.patch(f'/users/{user.id}', json={'name': 'test'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'name': 'test',
        'phone': 'tel:+55-11-4002-8922',
        'address': 'Rua dos Bobos, n° 0',
    }


def test_update_user_not_found(client):
    response = client.patch('/users/67', json={'name': 'test'})

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado.'}


def test_delete_user(client, user):
    response = client.delete(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Usuário deletado.'}


def test_delete_user_not_found(client):
    response = client.delete('/users/67')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado.'}
