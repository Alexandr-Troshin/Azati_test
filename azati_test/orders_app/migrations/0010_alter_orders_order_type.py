# Generated by Django 4.1.4 on 2022-12-26 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders_app', '0009_alter_orders_order_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='order_type',
            field=models.CharField(blank=True, choices=[('BUY', 'BUY'), ('SELL', 'SELL')], max_length=4, verbose_name='order_type'),
        ),
    ]
