# Generated by Django 3.0.7 on 2020-11-08 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0044_auto_20201108_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_form',
            field=models.IntegerField(choices=[(0, 'Наличные'), (1, 'Электронно')], null=True, verbose_name='способ оплаты'),
        ),
    ]
