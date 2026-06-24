from http import HTTPStatus

from flowops.models import UnitOfMeasure


def test_create_ingredient(client):
    response = client.post(
        '/ingredients/',
        json={
            'name': 'teste',
            'unit_of_measure': UnitOfMeasure.litro,
            'minimum': 7.5,
            'quantity': 0,
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'name': 'teste',
        'unit_of_measure': UnitOfMeasure.litro.value,
        'minimum': '7.5000000000',
        'quantity': '0E-10',
    }


def test_create_ingredient_conflict(client, ingredient):
    response = client.post(
        '/ingredients/',
        json={
            'name': ingredient.name,
            'unit_of_measure': UnitOfMeasure.litro,
            'minimum': 7.5,
            'quantity': 0,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Ingrediente já cadastrado.'}


def test_list_ingredients(client, ingredient):
    response = client.get('/ingredients/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'ingredients': [
            {
                'id': 1,
                'minimum': '10.0000000000',
                'name': 'ingrediente',
                'quantity': '0E-10',
                'unit_of_measure': 'Unidade(s)',
            }
        ]
    }


def test_list_ingredients_empty(client):
    response = client.get('/ingredients/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'ingredients': []}


def test_update_ingredient(client, ingredient):
    response = client.patch(
        f'/ingredients/{ingredient.id}', json={'name': 'test'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'minimum': '10.0000000000',
        'name': 'test',
        'quantity': '0E-10',
        'unit_of_measure': 'Unidade(s)',
    }


def test_update_ingredient_not_found(client):
    response = client.patch('/ingredients/67', json={'name': 'test'})

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Ingrediente não encontrado.'}


def test_delete_ingredient(client, ingredient):
    response = client.delete(f'/ingredients/{ingredient.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Ingrediente deletado.'}


def test_delete_ingredient_not_found(client):
    response = client.delete('/ingredients/67')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Ingrediente não encontrado.'}
