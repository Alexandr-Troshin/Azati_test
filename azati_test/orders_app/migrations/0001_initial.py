# Generated by Django 4.1.4 on 2023-01-25 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock', models.CharField(default='', max_length=30, verbose_name='stock')),
                ('shares', models.IntegerField(default=0, verbose_name='shares')),
                ('price_per_share', models.FloatField(default=0, verbose_name='price_per_share')),
                ('order_type', models.CharField(blank=True, choices=[('BUY', 'BUY'), ('SELL', 'SELL')], max_length=4, verbose_name='order_type')),
                ('order_dttm', models.DateTimeField(auto_now_add=True, null=True, verbose_name='order_dttm')),
            ],
            options={
                'db_table': 'orders',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock', models.CharField(default='', max_length=30, verbose_name='stock')),
                ('shares', models.IntegerField(default=0, verbose_name='shares')),
                ('price_per_share', models.FloatField(default=0, verbose_name='price_per_share')),
                ('buyer_name', models.CharField(default='', max_length=30, verbose_name='buyer_name')),
                ('seller_name', models.CharField(default='', max_length=30, verbose_name='seller_name')),
                ('trans_dttm', models.DateTimeField(auto_now_add=True, null=True, verbose_name='trans_dttm')),
            ],
            options={
                'db_table': 'transactions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TransLastOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock', models.CharField(default='', max_length=30, verbose_name='stock')),
                ('shares', models.IntegerField(default=0, verbose_name='shares')),
                ('price_per_share', models.FloatField(default=0, verbose_name='price_per_share')),
                ('order_type', models.CharField(default='BUY', max_length=4, verbose_name='order_type')),
                ('sum_shares', models.IntegerField(default=0, verbose_name='sum_shares')),
                ('order_dttm', models.DateTimeField(auto_now_add=True, null=True, verbose_name='order_dttm')),
            ],
            options={
                'db_table': 'trans_last_order',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OrdersDjango',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock', models.CharField(default='', max_length=30, verbose_name='stock')),
                ('shares', models.IntegerField(default=0, verbose_name='shares')),
                ('price_per_share', models.FloatField(default=0, verbose_name='price_per_share')),
                ('order_type', models.CharField(blank=True, choices=[('BUY', 'BUY'), ('SELL', 'SELL')], max_length=4, verbose_name='order_type')),
                ('order_dttm', models.DateTimeField(auto_now_add=True, null=True, verbose_name='order_dttm')),
            ],
            options={
                'db_table': 'orders_django',
            },
        ),
        migrations.CreateModel(
            name='OrdersDjangoLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.IntegerField(default=0, verbose_name='order_id')),
                ('stock', models.CharField(default='', max_length=30, verbose_name='stock')),
                ('shares', models.IntegerField(default=0, verbose_name='shares')),
                ('price_per_share', models.FloatField(default=0, verbose_name='price_per_share')),
                ('order_type', models.CharField(blank=True, choices=[('BUY', 'BUY'), ('SELL', 'SELL')], max_length=4, verbose_name='order_type')),
                ('order_dttm', models.DateTimeField(auto_now_add=True, null=True, verbose_name='order_dttm')),
                ('order_action', models.CharField(default='PUT', max_length=6, verbose_name='order_action')),
            ],
            options={
                'db_table': 'orders_django_log',
            },
        ),
        migrations.CreateModel(
            name='TransactionsDjango',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock', models.CharField(default='', max_length=30, verbose_name='stock')),
                ('shares', models.IntegerField(default=0, verbose_name='shares')),
                ('price_per_share', models.FloatField(default=0, verbose_name='price_per_share')),
                ('buyer_name', models.CharField(default='', max_length=30, verbose_name='buyer_name')),
                ('seller_name', models.CharField(default='', max_length=30, verbose_name='seller_name')),
                ('trans_dttm', models.DateTimeField(auto_now_add=True, null=True, verbose_name='trans_dttm')),
            ],
            options={
                'db_table': 'transactions_django',
            },
        ),
    ]
