from django.db import models


# классы таблиц для бизнес-логики в Django

class OrdersDjango(models.Model):
    """ Модель данных о заказах (используя бизнес-логику в Django)"""
    class Meta:
        db_table = 'orders_django'

#     if request.POST:


    ORDER_TYPE_CHOICES = [
        ('BUY', 'BUY'),
        ('SELL', 'SELL')
    ]

    id = models.IntegerField
    user_name = models.CharField('user_name', max_length=30, default='')
    stock = models.CharField('stock', max_length=30, default='')
    shares = models.IntegerField('shares', default=0)
    price_per_share = models.FloatField('price_per_share', default=0)
    order_type = models.CharField('order_type', max_length=4,
                                  choices=ORDER_TYPE_CHOICES,
                                  blank=True)
    order_dttm = models.DateTimeField('order_dttm', auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.user_name) + str(self.order_dttm)

class TransactionsDjango(models.Model):
    """ Модель данных о проведенных транзакциях (используя бизнес-логику в Django)"""
    class Meta:
        db_table = 'transactions_django'

    stock = models.CharField('stock', max_length=30, default='')
    shares = models.IntegerField('shares', default=0)
    price_per_share = models.FloatField('price_per_share', default=0)
    buyer_name = models.CharField('buyer_name', max_length=30, default='')
    seller_name = models.CharField('seller_name', max_length=30, default='')
    trans_dttm = models.DateTimeField('trans_dttm', auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.stock) + str(self.trans_dttm)

class OrdersDjangoLog(models.Model):
    """ Модель для логгирования данных о заказах (используя бизнес-логику в Django)"""
    class Meta:
        db_table = 'orders_django_log'

    ORDER_TYPE_CHOICES = [
        ('BUY', 'BUY'),
        ('SELL', 'SELL')
    ]

    id = models.IntegerField
    order_id = models.IntegerField('order_id', default=0)
    user_name = models.CharField('user_name', max_length=30, default='')
    stock = models.CharField('stock', max_length=30, default='')
    shares = models.IntegerField('shares', default=0)
    price_per_share = models.FloatField('price_per_share', default=0)
    order_type = models.CharField('order_type', max_length=4,
                                  choices=ORDER_TYPE_CHOICES,
                                  blank=True)
    order_dttm = models.DateTimeField('order_dttm', auto_now_add=True, null=True, blank=True)
    order_action = models.CharField('order_action', max_length=6, default='PUT')

    def __str__(self):
        return str(self.user_name) + str(self.order_dttm)

# классы таблиц для варианта с триггером
class Orders(models.Model):
    """ Модель данных о заказах (используя триггеры в Postgres)"""
    class Meta:
        db_table = 'orders'
        managed = False

    ORDER_TYPE_CHOICES = [
        ('BUY', 'BUY'),
        ('SELL', 'SELL')
    ]

    id = models.IntegerField
    user_name = models.CharField('user_name', max_length=30, default='')
    stock = models.CharField('stock', max_length=30, default='')
    shares = models.IntegerField('shares', default=0)
    price_per_share = models.FloatField('price_per_share', default=0)
    order_type = models.CharField('order_type', max_length=4,
                                  choices=ORDER_TYPE_CHOICES,
                                  blank=True)
    order_dttm = models.DateTimeField('order_dttm', auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.user_name) + str(self.order_dttm)


class Transactions(models.Model):
    """ Модель данных о проведенных транзакциях (используя триггеры в Postgres)"""
    class Meta:
        db_table = 'transactions'
        managed = False

    stock = models.CharField('stock', max_length=30, default='')
    shares = models.IntegerField('shares', default=0)
    price_per_share = models.FloatField('price_per_share', default=0)
    buyer_name = models.CharField('buyer_name', max_length=30, default='')
    seller_name = models.CharField('seller_name', max_length=30, default='')
    trans_dttm = models.DateTimeField('trans_dttm', auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.stock) + str(self.trans_dttm)


class TransLastOrder(models.Model):
    """ Модель промежуточной таблицы, данные о заказах, которые должны обработаться
    триггерами при добавлении нового заказа (используя триггеры в Postgres)
    (Заказы, имеющие нужный stock, противоположного направления (например, BUY при новом заказе SELL),
    подходящие по условиям стоимости. Отбираются только те заказы, которые полностью перекрываются
     транзакциями и следующий после них заказ, в котором транзакией закрывается только часть"""

    class Meta:
        db_table = 'trans_last_order'
        managed = False

    user_name = models.CharField('user_name', max_length=30, default='')
    stock = models.CharField('stock', max_length=30, default='')
    shares = models.IntegerField('shares', default=0)
    price_per_share = models.FloatField('price_per_share', default=0)
    order_type = models.CharField('order_type', max_length=4,
                                  # choices=ORDER_TYPE_CHOICES,
                                  default='BUY')
    sum_shares = models.IntegerField('sum_shares', default=0)
    order_dttm = models.DateTimeField('order_dttm', auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.user_name) + str(self.order_dttm)