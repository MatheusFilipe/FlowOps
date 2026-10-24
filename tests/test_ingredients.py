from http import HTTPStatus

from flowops.models import IngredientStatus, UnitOfMeasure


def test_create_ingredient_ok(client):
    response = client.post(
        '/ingredients/',
        json={
            'name': 'teste',
            'unit_of_measure': UnitOfMeasure.litro,
            'minimum': 7.5,
            'quantity': 10,
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'name': 'teste',
        'unit_of_measure': UnitOfMeasure.litro.value,
        'minimum': 7.5,
        'quantity': 10,
        'status': IngredientStatus.ok,
    }


def test_create_ingredient_low_stock(client):
    response = client.post(
        '/ingredients/',
        json={
            'name': 'teste',
            'unit_of_measure': UnitOfMeasure.litro,
            'minimum': 7.5,
            'quantity': 5,
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'name': 'teste',
        'unit_of_measure': UnitOfMeasure.litro.value,
        'minimum': 7.5,
        'quantity': 5,
        'status': IngredientStatus.low_stock,
    }


def test_create_ingredient_out_of_stock(client):
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
        'minimum': 7.5,
        'quantity': 0,
        'status': IngredientStatus.out_of_stock,
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


def test_create_ingredient_negative_quantity(client):
    response = client.post(
        '/ingredients/',
        json={
            'name': 'teste',
            'unit_of_measure': UnitOfMeasure.litro,
            'minimum': 7.5,
            'quantity': -1,
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == {'detail': 'A quantidade não pode ser negativa.'}


def test_list_ingredients(client, ingredient):
    response = client.get('/ingredients/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'ingredients': [
            {
                'id': 1,
                'minimum': 10,
                'name': 'ingredient',
                'quantity': 20,
                'unit_of_measure': 'Unidade(s)',
                'status': IngredientStatus.ok,
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
        'minimum': 10,
        'name': 'test',
        'quantity': 20,
        'unit_of_measure': 'Unidade(s)',
        'status': IngredientStatus.ok,
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
