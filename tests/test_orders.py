from http import HTTPStatus

from flowops.models import IngredientStatus, Order, OrderStatus


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
        'status': 'Em fila de espera',
        'ingredients_qty': {'1': 10.0}
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


def test_create_order_insufficient_stock(client, user, product):
    quantity = 67
    response = client.post(
        '/orders/',
        json={
            'client_id': user.id,
            'notes': 'notes',
            'product_quantity': {product.id: quantity},
        },
    )

    product_ingredient = [p_i for p_i in product.product_ingredients][0]
    ingredient = product_ingredient.ingredient
    required_qty = product_ingredient.quantity * quantity

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == {
        'detail': (
            f'Estoque insuficiente para o ingrediente '
            f'"{ingredient.name}". Disponível: {ingredient.quantity}. '
            f'Requerido: {required_qty}.'
        )
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
    assert response.json() == {
        'detail': 'Um ou mais ingredientes não foram encontrados.'
    }


def test_subtract_ingredients_from_stock(client, user, ingredient, product):
    initial_quantity = ingredient.quantity

    response = client.post(
        '/orders/',
        json={
            'client_id': user.id,
            'notes': 'notes',
            'product_quantity': {product.id: 1},
        },
    )

    final_quantity = product.product_ingredients[0].ingredient.quantity

    assert response.status_code == HTTPStatus.OK
    assert final_quantity == (
        initial_quantity - product.product_ingredients[0].quantity
    )


def test_check_ingredient_status_when_subtract_ok(
    client, user, ingredient, product
):
    initial_status = ingredient.status
    client.post(
        '/orders/',
        json={
            'client_id': user.id,
            'notes': 'notes',
            'product_quantity': {product.id: 1},
        },
    )
    final_status = ingredient.status

    assert initial_status == IngredientStatus.ok
    assert final_status == IngredientStatus.ok


def test_check_ingredient_status_when_subtract_low_stock(
    client, user, ingredient, product
):
    initial_status = ingredient.status
    client.post(
        '/orders/',
        json={
            'client_id': user.id,
            'notes': 'notes',
            'product_quantity': {product.id: 3},
        },
    )
    final_status = ingredient.status

    assert initial_status == IngredientStatus.ok
    assert final_status == IngredientStatus.low_stock


def test_check_ingredient_status_when_subtract_out_of_stock(
    client, user, ingredient, product
):
    initial_status = ingredient.status
    client.post(
        '/orders/',
        json={
            'client_id': user.id,
            'notes': 'notes',
            'product_quantity': {product.id: 4},
        },
    )
    final_status = ingredient.status

    assert initial_status == IngredientStatus.ok
    assert final_status == IngredientStatus.out_of_stock


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
                'status': 'Em fila de espera',
                'ingredients_qty': {'1': 10.0}
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


def test_cancel_order(client, order):
    response = client.post(
        f'/orders/{order.id}', json={'reason': 'Tempo de espera.'}
    )

    assert response.status_code == HTTPStatus.OK
    assert order.status == OrderStatus.canceled
    assert response.json() == {'reason': 'Tempo de espera.'}


def test_cancel_order_not_found(client):
    response = client.post('/orders/67', json={'reason': '.'})

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Pedido não encontrado.'}


def test_cancel_order_being_prepared(client, order):
    order.status = OrderStatus.being_prepared
    response = client.post(
        f'/orders/{order.id}', json={'reason': 'Tempo de espera.'}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': (
            'O pedido não pode ser cancelado porque já está em preparação.'
        )
    }


def test_cancel_order_completed(client, order):
    order.status = OrderStatus.completed
    response = client.post(
        f'/orders/{order.id}', json={'reason': 'Tempo de espera.'}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == {
        'detail': 'O pedido não pode ser cancelado porque já está finalizado.'
    }


def test_cancel_order_canceled(client, order):
    order.status = OrderStatus.canceled
    response = client.post(
        f'/orders/{order.id}', json={'reason': 'Tempo de espera.'}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'O pedido não pode ser cancelado porque já está cancelado.'
    }


def test_restock_ingredients(client, user, ingredient, product):
    initial_quantity = ingredient.quantity

    order_response = client.post(
        '/orders/',
        json={
            'client_id': user.id,
            'notes': 'notes',
            'product_quantity': {product.id: 1},
        },
    )
    order = order_response.json()

    subtract = product.product_ingredients[0].ingredient.quantity

    client.post(f'/orders/{order["id"]}', json={'reason': 'Tempo de espera.'})
    restock = product.product_ingredients[0].ingredient.quantity

    assert subtract == (
        initial_quantity - product.product_ingredients[0].quantity
    )
    assert restock == initial_quantity


def test_check_ingredient_status_when_restock(
    client, user, ingredient, product
):
    initial_status = ingredient.status

    order_response = client.post(
        '/orders/',
        json={
            'client_id': user.id,
            'notes': 'notes',
            'product_quantity': {product.id: 3},
        },
    )
    order = order_response.json()

    client.post(f'/orders/{order["id"]}', json={'reason': 'Tempo de espera.'})
    final_status = ingredient.status

    assert initial_status == final_status
