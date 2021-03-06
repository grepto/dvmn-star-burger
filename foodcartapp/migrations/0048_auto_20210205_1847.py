# Generated by Django 3.0.7 on 2021-02-05 18:47

from django.db import migrations
from phonenumber_field.modelfields import PhoneNumberField


def normalize_phone_numbers(apps, schema_editor):
    Order = apps.get_model('foodcartapp', 'Order')
    for item in Order.objects.all().iterator():
        item.formatted_phonenumber = PhoneNumberField().get_prep_value(item.phonenumber)
        item.save()


def move_backward(apps, schema_editor):
    Order = apps.get_model('foodcartapp', 'Order')
    for item in Order.objects.all().iterator():
        item.formatted_phonenumber = ''
        item.save()


class Migration(migrations.Migration):
    dependencies = [
        ('foodcartapp', '0047_order_formatted_phonenumber'),
    ]

    operations = [
        migrations.RunPython(normalize_phone_numbers, move_backward)
    ]
