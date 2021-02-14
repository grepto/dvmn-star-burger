from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField('контактный телефон', max_length=50, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'


class ProductQuerySet(models.QuerySet):
    def available(self):
        return self.distinct().filter(menu_items__availability=True)


class ProductCategory(models.Model):
    name = models.CharField('название', max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('название', max_length=50)
    category = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL,
                                 verbose_name='категория', related_name='products')
    price = models.DecimalField('цена', max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField('картинка')
    special_status = models.BooleanField('спец.предложение', default=False, db_index=True)
    description = models.TextField('описание', max_length=200, blank=True)

    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items',
                                   verbose_name="ресторан")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='menu_items',
                                verbose_name='продукт')
    availability = models.BooleanField('в продаже', default=True, db_index=True)

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]


class OrderQuerySet(models.QuerySet):
    def with_total_price(self):
        return self.annotate(price=Sum('order_items__price'))


class Order(models.Model):
    NEW = 0
    COOKING = 1
    DELIVERY = 2
    DELIVERED = 3

    CASH = 0
    CARD = 1

    STATUS_CHOICES = [
        (NEW, 'Необработанный'),
        (COOKING, 'Готовится'),
        (DELIVERY, 'На доставке'),
        (DELIVERED, 'Доставлен'),
    ]

    PAYMENT_FORM_CHOICES = [
        (CASH, 'Наличные'),
        (CARD, 'Электронно'),
    ]

    orders = OrderQuerySet.as_manager()

    status = models.IntegerField('статус', choices=STATUS_CHOICES, default=0)
    payment_form = models.IntegerField('способ оплаты', choices=PAYMENT_FORM_CHOICES, null=True)
    firstname = models.CharField('имя', max_length=100)
    lastname = models.CharField('фамилия', max_length=100)
    original_phonenumber = models.CharField('номер телефона', max_length=100)
    phonenumber = PhoneNumberField('номер телефона')
    address = models.TextField('адрес доставки', max_length=8000)
    comment = models.TextField('комментарий', blank=True)
    registered_at = models.DateTimeField('создан', default=timezone.now)
    called_at = models.DateTimeField('звонок', blank=True, null=True)
    delivered_at = models.DateTimeField('доставлен', blank=True, null=True)

    def __str__(self):
        return f"{self.lastname} {self.firstname} - {self.phonenumber}"

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items', verbose_name='заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items', verbose_name='продукт')
    quantity = models.PositiveSmallIntegerField('количество', validators=[MinValueValidator(1)])
    price = models.PositiveSmallIntegerField('Стоимость', validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.product.name} - {self.quantity} шт.  - {self.order}"

    class Meta:
        verbose_name = 'пункт заказа'
        verbose_name_plural = 'пункты заказа'
