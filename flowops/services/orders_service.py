from collections import Counter

from sqlalchemy import select

from flowops.models import Product


async def list_products(session):
    products = await session.scalars(select(Product))  # group by tag

    message = ''
    for product in products:
        message += f'{product.id}: {product.name}\n'
        if product.description:
            message += f'- {product.description}\n'

    return message


async def add_product_to_order(session, order_items, id):
    new_order = order_items.copy()
    new_order.append(
        await session.scalar(select(Product).where(Product.id == id))
    )

    return new_order


async def delete_product_from_order(session, order_items, product_id):
    new_order = order_items.copy()
    new_order.remove(
        await session.scalar(select(Product).where(Product.id == product_id))
    )

    return new_order


async def read_order(session, order_items):
    product_names = [product.name for product in order_items]
    product_quantity = Counter(product_names)
    message = ''

    for product, quantity in product_quantity.items():
        message += f'- {quantity} {product}\n'

    return message
