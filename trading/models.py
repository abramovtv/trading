# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, IntegrityError


class Trader(models.Model):
    name = models.CharField(u"Имя", max_length=30)
    balance = models.DecimalField(u"Баланс", max_digits=12, decimal_places=2, default=0)
    total_profit = models.DecimalField(u"Общая прибыль", max_digits=12, decimal_places=2, default=0)
    total_deposit = models.DecimalField(u"Общий депозит", max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return "({}) {}".format(self.pk, self.name)

    def __unicode__(self):
        return self.__str__()

    class Meta:
        verbose_name = u"Трейдер"
        verbose_name_plural = u"Трейдеры"


class Deal(models.Model):
    trader = models.ForeignKey(Trader, related_name='deals')
    amount = models.DecimalField(u"Сумма", max_digits=12, decimal_places=2)
    result_amount = models.DecimalField(u"Результат", max_digits=12, decimal_places=2)
    time = models.DateTimeField(u"Время", db_index=True, auto_created=True)

    def save(self, *args, **kwargs):
        # if self.pk:
        #     raise NotImplemented(u"Невозможно перезаписать финансовую информацию")

        super(Deal, self).save(*args, **kwargs)

        Trader.objects.filter(
            pk=self.trader_id
        ).update(
            total_profit=models.F('total_profit') + self.result_amount
        )

        try:
            DealStat.objects.create(  # create_or_update не подойдет из-за возможности потери данных при race condition
                trader=self.trader, time=self.time.date(), amount=self.amount, result_amount=self.result_amount
            )
        except IntegrityError:
            DealStat.objects.filter(
                trader=self.trader, time=self.time.date()
            ).update(
                amount=models.F('amount')+self.amount,
                result_amount=models.F('result_amount')+self.result_amount
            )

    # def delete(self, using=None, keep_parents=False):
    #     raise NotImplemented(u"Невозможно удалить финансовую информацию")

    def __str__(self):
        return "({}) {}: {}/{}".format(self.pk, self.trader_id, self.amount, self.result_amount)

    def __unicode__(self):
        return self.__str__()

    class Meta:
        verbose_name = u"Сделка"
        verbose_name_plural = u"Сделки"


class Transaction(models.Model):
    DEPOSIT = 1
    WITHDRAWAL = 2
    TRANSACTION_TYPES = (
        (DEPOSIT, u'Депозит'),
        (WITHDRAWAL, u'Вывод'),
    )
    trader = models.ForeignKey(Trader, related_name='transactions')
    amount = models.DecimalField(u"Сумма", max_digits=12, decimal_places=2)
    type = models.SmallIntegerField(u"Тип транзакции", choices=TRANSACTION_TYPES)
    time = models.DateTimeField(u"Время", auto_created=True)

    @property
    def real_amount(self):
        return self.amount if self.is_deposit else -self.amount

    @property
    def is_deposit(self):
        return self.type==Transaction.DEPOSIT

    def save(self, *args, **kwargs):
        # if self.pk:
        #     raise NotImplemented(u"Невозможно перезаписать финансовую информацию")

        super(Transaction, self).save(*args, **kwargs)

        params = {'balance': models.F('balance')+self.real_amount}
        if self.is_deposit:
            params['total_deposit'] = models.F('total_deposit')+self.amount

        Trader.objects.filter(pk=self.trader_id).update(**params)

    # def delete(self, using=None, keep_parents=False):
    #     raise NotImplemented(u"Невозможно удалить финансовую информацию")

    def __str__(self):
        return "({}) {}: {} {}".format(
            self.pk, self.trader_id, self.get_type_display(), self.amount,
        )

    def __unicode__(self):
        return self.__str__()

    class Meta:
        verbose_name = u"Транзакция"
        verbose_name_plural = u"Транзакции"
        index_together = (
            ('type', 'trader', 'amount')
        )


class DealStat(models.Model):
    trader = models.ForeignKey(Trader, related_name='dealstats')
    amount = models.DecimalField(u"Сумма", max_digits=12, decimal_places=2)
    result_amount = models.DecimalField(u"Результат", max_digits=12, decimal_places=2)
    time = models.DateField(u"Время", auto_created=True)

    def __str__(self):
        return "({}) {} {}: {}/{}".format(self.pk, self.trader_id, self.time, self.amount, self.result_amount)

    def __unicode__(self):
        return self.__str__()

    class Meta:
        verbose_name = u"Статистика"
        verbose_name_plural= u"Статистика"
        unique_together = (
            ('time', 'trader')
        )
