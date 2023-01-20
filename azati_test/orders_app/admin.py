from django.contrib import admin
from .models import Orders, TransLastOrder, Transactions, \
                    OrdersDjango, OrdersDjangoLog, TransactionsDjango

admin.site.register(Orders)
admin.site.register(TransLastOrder)
admin.site.register(Transactions)

admin.site.register(OrdersDjango)
admin.site.register(OrdersDjangoLog)
admin.site.register(TransactionsDjango)