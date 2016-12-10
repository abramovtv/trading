# -*- coding: utf-8 -*-
import random
from decimal import Decimal
from itertools import chain, islice

from datetime import timedelta, date, time, datetime
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from trading.models import *
from django.db.models import F, Max


class Command(BaseCommand):
    help = 'Generate test data'

    names = ["Noah", "Liam", "Mason", "Jacob", "William", "Ethan", "James", "Alexander", "Michael", "Benjamin",
             "Elijah", "Daniel", "Aiden", "Logan", "Matthew", "Lucas", "Jackson", "David", "Oliver", "Jayden", "Joseph",
             "Gabriel", "Samuel", "Carter", "Anthony", "John", "Dylan", "Luke", "Henry", "Andrew", "Isaac",
             "Christopher", "Joshua", "Wyatt", "Sebastian", "Owen", "Caleb", "Nathan", "Ryan", "Jack", "Hunter", "Levi",
             "Christian", "Jaxon", "Julian", "Landon", "Grayson", "Jonathan", "Isaiah", "Charles", "Thomas", "Aaron",
             "Eli", "Connor", "Jeremiah", "Cameron", "Josiah", "Adrian", "Colton", "Jordan", "Brayden", "Nicholas",
             "Robert", "Angel", "Hudson", "Lincoln", "Evan", "Dominic", "Austin", "Gavin", "Nolan", "Parker", "Adam",
             "Chase", "Jace", "Ian", "Cooper", "Easton", "Kevin", "Jose", "Tyler", "Brandon", "Asher", "Jaxson",
             "Mateo", "Jason", "Ayden", "Zachary", "Carson", "Xavier", "Leo", "Ezra", "Bentley", "Sawyer", "Kayden",
             "Blake", "Nathaniel", "Ryder", "Theodore", "Elias", "Emma", "Olivia", "Sophia", "Ava", "Isabella", "Mia",
             "Abigail", "Emily", "Charlotte", "Harper", "Madison", "Amelia", "Elizabeth", "Sofia", "Evelyn", "Avery",
             "Chloe", "Ella", "Grace", "Victoria", "Aubrey", "Scarlett", "Zoey", "Addison", "Lily", "Lillian",
             "Natalie", "Hannah", "Aria", "Layla", "Brooklyn", "Alexa", "Zoe", "Penelope", "Riley", "Leah", "Audrey",
             "Savannah", "Allison", "Samantha", "Nora", "Skylar", "Camila", "Anna", "Paisley", "Ariana", "Ellie",
             "Aaliyah", "Claire", "Violet", "Stella", "Sadie", "Mila", "Gabriella", "Lucy", "Arianna", "Kennedy",
             "Sarah", "Madelyn", "Eleanor", "Kaylee", "Caroline", "Hazel", "Hailey", "Genesis", "Kylie", "Autumn",
             "Piper", "Maya", "Nevaeh", "Serenity", "Peyton", "Mackenzie", "Bella", "Eva", "Taylor", "Naomi", "Aubree",
             "Aurora", "Melanie", "Lydia", "Brianna", "Ruby", "Katherine", "Ashley", "Alexis", "Alice", "Cora", "Julia",
             "Madeline", "Faith", "Annabelle", "Alyssa", "Isabelle", "Vivian", "Gianna", "Quinn", "Clara", "Reagan",
             "Khloe"]

    surnames = ["Smith", "Jones", "Williams", "Taylor", "Brown", "Davies", "Evans", "Wilson", "Thomas", "Johnson",
                "Roberts", "Robinson", "Thompson", "Wright", "Walker", "White", "Edwards", "Hughes", "Green", "Hall",
                "Lewis", "Harris", "Clarke", "Patel", "Jackson"]

    def add_arguments(self, parser):
        parser.add_argument('-t', dest='traders', type=int, default=1000000)
        parser.add_argument('-r', dest='transactions', type=int, default=5)
        parser.add_argument('-a', dest='active', type=int, default=1000)
        parser.add_argument('-d', dest='deals', type=int, default=100)
        parser.add_argument('-s', dest='dates', type=int, default=365*3)

    def chunks(self, iterable, size=1000):
        iterator = iter(iterable)
        for first in iterator:
            yield chain([first], islice(iterator, size - 1))

    def handle(self, *args, **options):
        now = timezone.now()

        if options['traders']:
            print 'traders ',
            traders = (Trader(name="{} {}".format(
                random.choice(self.names), random.choice(self.surnames))
            ) for i in xrange(options['traders']))

            for chunk in self.chunks(traders, 1000):
                print '.',
                Trader.objects.bulk_create(chunk)
            print

        if options['transactions']:
            print 'transactions ',
            for trader_ids in self.chunks(Trader.objects.values_list('id', flat=True), 100):
                transactions = []
                for trader_id in trader_ids:
                    if random.random()>0.9:
                        continue

                    balance, total_deposit = 0.0, 0.0

                    for i in xrange(options['transactions']):
                        transaction = Transaction(
                            trader_id=trader_id,
                            amount=round(random.random() * 1000, 2),
                            type=i and random.randint(1, 2) or 1,
                            time=now - timedelta(seconds=random.randrange(options['dates'] * 86400))
                        )
                        balance += transaction.real_amount
                        if transaction.is_deposit:
                            total_deposit += transaction.amount

                        transactions.append(transaction)

                    Trader.objects.filter(id=trader_id).update(
                        balance=F('balance')+Decimal(str(balance)),
                        total_deposit=F('total_deposit')+Decimal(str(total_deposit))
                    )
                    if not trader_id%1000:
                        print

                Transaction.objects.bulk_create(transactions)
                print '.',
            print

        if options['deals']:
            max_trader_id = Trader.objects.all().aggregate(Max('id'))['id__max']

            print 'deals ',
            for day in xrange(options['dates']):
                now = datetime.combine(date.today(), time())-timedelta(days=day)
                trader_ids = set(random.randint(1, max_trader_id) for i in xrange(options['active']))

                for trader_id in trader_ids:
                    amount, result_amount = 0.0, 0.0
                    deals = []
                    for i in xrange(options['deals']):
                        deal = Deal(
                            trader_id=trader_id,
                            amount=round(random.random() * 1000, 2),
                            result_amount=round(random.random() * 100 - 51, 2),
                            time =timezone.make_aware(now + timedelta(seconds=random.randrange(86399)))
                        )
                        amount += deal.amount
                        result_amount += deal.result_amount
                        deals.append(deal)

                    Deal.objects.bulk_create(deals)
                    amount = Decimal(str(amount))
                    result_amount = Decimal(str(result_amount))

                    Trader.objects.filter(id=trader_id).update(
                        balance=F('balance')+result_amount,
                        total_profit=F('total_profit')+result_amount
                    )

                    try:
                        DealStat.objects.create(
                            trader_id=trader_id, time = now.date(),
                            amount=amount, result_amount=result_amount
                        )
                    except IntegrityError:
                        DealStat.objects.filter(
                            trader_id=trader_id, time=now.date(),
                        ).update(
                            amount=models.F('amount') + amount,
                            result_amount=models.F('result_amount') + result_amount
                        )
                print '.',
                if not day%100:
                    print
            print

