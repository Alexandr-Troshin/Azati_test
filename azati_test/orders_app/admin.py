from django.contrib import admin
from .models import Orders, TransLastOrder, Transactions

admin.site.register(Orders)
admin.site.register(TransLastOrder)
admin.site.register(Transactions)