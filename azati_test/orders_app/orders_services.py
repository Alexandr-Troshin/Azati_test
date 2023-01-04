from django.db.models import QuerySet
from .models import OrdersDjango, TransactionsDjango


def get_counter_orders_list(order_details: dict) -> QuerySet:
    """Функция возвращает queryset встречных заказов,
    с которыми можно провести транзакцию"""
    filtered_queryset = OrdersDjango.objects \
        .exclude(user_name=order_details['user_name']) \
        .exclude(order_type=order_details['order_type']) \
        .filter(stock=order_details['stock'])
    if order_details['order_type'] == 'SELL':
        filtered_meet_price_requirements_queryset = filtered_queryset \
            .filter(price_per_share__gte=order_details['price_per_share'])
        sorting_order = '-price_per_share'
    else:
        filtered_meet_price_requirements_queryset = filtered_queryset \
            .filter(price_per_share__lte=order_details['price_per_share'])
        sorting_order = 'price_per_share'
    return filtered_meet_price_requirements_queryset.order_by(sorting_order, 'order_dttm')


def prepare_dict_with_details_from_post_request(request) -> dict:
    order_details = request.POST.dict()
    order_details['shares'] = int(order_details['shares'])
    order_details['price_per_share'] = float(order_details['price_per_share'])
    del order_details['csrfmiddlewaretoken']
    return order_details


def _make_transaction(order_details, counter_order) -> None:
    transaction_details = {'stock': order_details['stock'],
                           'shares': min(order_details['shares'],
                                         counter_order.get('shares')),
                           'price_per_share': (order_details['price_per_share']
                                               + counter_order.get('price_per_share')) / 2}
    if order_details['order_type'] == 'SELL':
        transaction_details['seller_name'] = order_details['user_name']
        transaction_details['buyer_name'] = counter_order['user_name']
    else:
        transaction_details['buyer_name'] = order_details['user_name']
        transaction_details['seller_name'] = counter_order['user_name']
    TransactionsDjango.objects.create(**transaction_details)


def make_trasactions_and_update_orders_list(order_details, counter_orders_list, created_order_id) -> None:
    for counter_order in counter_orders_list:
        _make_transaction(order_details, counter_order)
        if order_details['shares'] >= counter_order['shares']:
            order_details['shares'] -= counter_order['shares']
            OrdersDjango.objects.filter(pk=counter_order['id']).delete()
        else:
            OrdersDjango.objects.filter(pk=counter_order['id']). \
                update(shares=(counter_order['shares'] - order_details['shares']))
            order_details['shares'] = 0
        if order_details['shares'] == 0:
            OrdersDjango.objects.filter(pk=created_order_id) \
                .update(shares=0)
            OrdersDjango.objects.filter(pk=created_order_id).delete()
            break
    if order_details['shares'] > 0:
        OrdersDjango.objects.filter(pk=created_order_id) \
            .update(shares=order_details['shares'])
