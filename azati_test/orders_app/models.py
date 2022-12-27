from django.db import models


class Orders(models.Model):
    class Meta:
        db_table = 'orders'

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

    class Meta:
        db_table = 'transactions'

    stock = models.CharField('stock', max_length=30, default='')
    shares = models.IntegerField('shares', default=0)
    price_per_share = models.FloatField('price_per_share', default=0)
    buyer_name = models.CharField('buyer_name', max_length=30, default='')
    seller_name = models.CharField('seller_name', max_length=30, default='')
    trans_dttm = models.DateTimeField('trans_dttm', auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.stock) + str(self.trans_dttm)


class TransLastOrder(models.Model):


    class Meta:
        db_table = 'trans_last_order'

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