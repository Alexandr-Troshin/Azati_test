# Generated by Django 4.1.4 on 2022-12-26 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders_app', '0008_rename_trans_last_order_translastorder_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='order_type',
            field=models.CharField(choices=[('BUY', 'BUY'), ('SELL', 'SELL')], max_length=4, verbose_name='order_type'),
        ),
    ]
