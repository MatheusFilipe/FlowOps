from http import HTTPStatus

from flowops.schemas import ProductPublic


def test_create_product(client, ingredient):
    response = client.post(
        '/products/',
        json={
            'name': 'product',
            'description': 'description',
            'preparation_time': 15,
            'ingredients_quantity': {ingredient.id: 5},
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'name': 'product',
        'description': 'description',
        'preparation_time': 15,
    }


def test_create_product_conflict(client, product, ingredient):
    response = client.post(
        '/products/',
        json={
            'name': 'product',
            'description': 'description',
            'preparation_time': 15,
            'ingredients_quantity': {ingredient.id: 5},
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Produto já cadastrado.'}


def test_create_product_ingredient_not_found(client):
    response = client.post(
        '/products/',
        json={
            'name': 'product',
            'description': 'description',
            'preparation_time': 15,
            'ingredients_quantity': {67: 5},
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Ingrediente não encontrado.'}


def test_list_products(client, product):
    response = client.get('/products/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'products': [ProductPublic.model_validate(product).model_dump()]
    }


def test_list_products_empty(client):
    response = client.get('/products/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'products': []}


def test_update_product(client, product):
    response = client.patch(f'/products/{product.id}', json={'name': 'test'})

    payload = ProductPublic.model_validate(product).model_dump()
    payload['name'] = 'test'

    assert response.status_code == HTTPStatus.OK
    assert response.json() == payload


def test_update_product_not_found(client):
    response = client.patch('/products/67', json={'name': 'test'})

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Produto não encontrado.'}


def test_delete_product(client, product):
    response = client.delete(f'/products/{product.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Produto deletado.'}


def test_delete_product_not_found(client):
    response = client.delete('/products/67')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Produto não encontrado.'}
