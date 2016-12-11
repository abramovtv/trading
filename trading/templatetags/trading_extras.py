# -*- coding: utf-8 -*-
from decimal import Decimal
from django import template
from trading.helpers import moneyfmt

register = template.Library()


@register.filter(name='money')
def money(value, arg=""):
    # arg="places=2|curr=$|sep=,|dp=.|pos=|neg=-|trailneg="
    args = dict(tuple(pair.split("=")) for pair in arg.split('|'))
    return moneyfmt(Decimal(value), **args)
