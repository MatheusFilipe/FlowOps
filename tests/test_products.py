from http import HTTPStatus


def test_create_product(client, ingredient):
    response = client.post(
        '/products/',
        json={
            'name': 'product',
            'description': 'description',
            'preparation_time': 15,
            'price': 10,
            'ingredients_quantity': {ingredient.id: 5},
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'name': 'product',
        'description': 'description',
        'preparation_time': 15,
        'price': '10.0000000000',
    }


def test_create_product_conflict(client, product, ingredient):
    response = client.post(
        '/products/',
        json={
            'name': 'product',
            'description': 'description',
            'preparation_time': 15,
            'price': 10,
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
            'price': 10,
            'ingredients_quantity': {67: 5},
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Ingrediente não encontrado.'}


def test_list_products(client, product):
    response = client.get('/products/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'products': [
            {
                'description': 'description',
                'id': 1,
                'name': 'product',
                'preparation_time': 15,
                'price': '10.0000000000',
            }
        ]
    }


def test_list_products_empty(client):
    response = client.get('/products/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'products': []}


def test_update_product(client, product):
    response = client.patch(f'/products/{product.id}', json={'name': 'test'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'name': 'test',
        'description': 'description',
        'preparation_time': 15,
        'price': '10.0000000000',
    }


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
