from http import HTTPStatus

from flowops.models import Order


def test_create_order(client, user, product, mock_db_time):
    with mock_db_time(
        model=Order, order_preparation_time=product.preparation_time
    ):
        response = client.post(
            '/orders/',
            json={
                'client_id': user.id,
                'notes': 'notes',
                'product_quantity': {product.id: 2},
            },
        )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'notes': 'notes',
        'ordered_at': '2001-09-11T08:46:00',
        'final_amount': '20.0000000000',
        'estimated_ready_at': '2001-09-11T09:01:00',
    }


def test_create_order_client_not_found(client, product):
    response = client.post(
        '/orders/',
        json={
            'client_id': 67,
            'notes': 'notes',
            'product_quantity': {product.id: 2},
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Cliente não encontrado.'}


def test_create_order_product_not_found(client, user):
    response = client.post(
        '/orders/',
        json={
            'client_id': user.id,
            'notes': 'notes',
            'product_quantity': {67: 2},
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Produto não encontrado.'}


def test_create_order_missing_ingredients(
    client, user, product_insufficient_ingredient
):
    response = client.post(
        '/orders/',
        json={
            'client_id': user.id,
            'notes': 'notes',
            'product_quantity': {product_insufficient_ingredient.id: 1},
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {
        'detail': 'Quantidade de ingrediente em estoque insuficiente.'
    }


def test_create_order_not_found_ingredient(
    client, user, product_not_found_ingredient
):
    response = client.post(
        '/orders/',
        json={
            'client_id': user.id,
            'notes': 'notes',
            'product_quantity': {product_not_found_ingredient.id: 1},
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Ingrediente não encontrado.'}


def test_list_orders(client, order, user):
    response = client.get(f'/orders/{user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'orders': [
            {
                'id': 1,
                'notes': 'notes',
                'ordered_at': '2001-09-11T08:46:00',
                'final_amount': '20.0000000000',
                'estimated_ready_at': '2001-09-11T09:01:00',
            }
        ]
    }


def test_list_orders_empty(client, user):
    response = client.get(f'/orders/{user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'orders': []}


def test_list_orders_client_not_found(client):
    response = client.get('/orders/67')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Cliente não encontrado.'}


def test_delete_order(client, order):
    response = client.delete(f'/orders/{order.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Pedido cancelado.'}


def test_delete_order_not_found(client):
    response = client.delete('/orders/67')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Pedido não encontrado.'}
