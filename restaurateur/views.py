import copy

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from foodcartapp.models import Product, Restaurant
from foodcartapp.models import Order
from restaurateur.geocoder import get_distance

RESTAURANT_DISTANCE_CACHE_EXPIRE = 60 * 60 * 24 * 30


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:
        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    products = Product.objects.filter(menu_items__availability=True) \
        .prefetch_related('menu_items__restaurant') \
        .distinct()

    orders = Order.orders.with_total_price().prefetch_related('order_items__product')

    product_restaurants = {}
    for product in products.all():
        product_restaurants[product] = {menu_item.restaurant for menu_item in product.menu_items.all()}

    for order in orders:
        order_products = [order_item.product for order_item in order.order_items.all()]
        restaurants = [product_restaurants.get(product) for product in order_products]
        if restaurants:
            relevant_restaurants = copy.deepcopy(restaurants[0].intersection(*restaurants))
            for restaurant in relevant_restaurants:
                cached_distance = cache.get(f'{order.id}{restaurant.id}')
                if not cached_distance:
                    cached_distance = get_distance(settings.GEOCODER_APIKEY, order.address, restaurant.address)
                    cache.set(f'{order.id}{restaurant.id}', cached_distance)
                restaurant.distance = cached_distance
            order.restaurants = sorted(relevant_restaurants, key=lambda restaurant: restaurant.distance or 0)

    return render(request, template_name='orders.html', context={
        'orders': orders
    })
