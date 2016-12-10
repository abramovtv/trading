# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib import admin

from .views import AdminStatView
from .models import *


@admin.register(Trader)
class TraderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'balance', 'total_profit', 'total_deposit')


class TraderNameMixin(object):
    def trader_name(self, obj):
         return obj.trader.name
    trader_name.short_description=u"Трейдер"


@admin.register(Deal)
class DealAdmin(TraderNameMixin, admin.ModelAdmin):
    list_display = ('id', 'time', 'trader_name', 'amount', 'result_amount')
    raw_id_fields = ('trader',)
    list_select_related = ('trader',)
    show_full_result_count = False


@admin.register(DealStat)
class DealAdmin(TraderNameMixin, admin.ModelAdmin):
    list_display = ('id', 'time', 'trader_name', 'amount', 'result_amount')
    list_select_related = ('trader',)
    raw_id_fields = ('trader',)
    show_full_result_count = False


@admin.register(Transaction)
class TransactionAdmin(TraderNameMixin, admin.ModelAdmin):
    list_display = ('id', 'time', 'trader_name', 'type', 'amount')
    raw_id_fields = ('trader', )
    show_full_result_count = False

    """ select_related('trader') работает плохо, потмоу что он делает inner join таблиц, который почему-то пытается
       присоединить Transaction к Trader, а не наоборот и не использует индексы и делает какую-то жесть. Можно было бы
       сделать left join, который работает в данном случае правильно и выполняется моментом, но для этого надо в
       Transaction делать поле trader null=True, что мне не хочется. prefetch_related делает + 1 запрос, но быстрый
       """
    def get_queryset(self, request):
        return super(TraderNameMixin, self).get_queryset(request).prefetch_related('trader')

# @admin.register(DealStat)
# class MyModelAdmin(admin.ModelAdmin):
#     def get_urls(self):
#         urls = super(MyModelAdmin, self).get_urls()
#         my_urls = [
#             url(r'^stats/$', self.admin_site.admin_view(AdminStatView.as_view())),
#         ]
#         return my_urls + urls
