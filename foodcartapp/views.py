import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST', ])
def register_order(request):
    try:
        data = request.data
        if data.get('products') \
            and isinstance(data['products'], list) \
            and all([data.get('firstname'), data.get('lastname'), data.get('phonenumber'), data.get('address')]) \
            and all([Product.objects.filter(id=item['product']) for item in data.get('products')]) \
            and isinstance(data.get('firstname'), str):
            order = Order.objects.create(last_name=data['lastname'],
                                         first_name=data['firstname'],
                                         phone_number=data['phonenumber'],
                                         )
        else:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

        for item in data['products']:
            order.order_items.create(product_id=item['product'], quantity=item['quantity'])
        return Response(data, status=status.HTTP_201_CREATED)
    except ValueError:
        return Response(None, status=status.HTTP_400_BAD_REQUEST)
