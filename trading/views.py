from datetime import date
from django.db.models import Sum
from django.http import HttpResponse
from django.views.generic import ListView

from .models import DealStat


def index(request):
    return HttpResponse("Trading index.")

class DealStatView(ListView):
    template_name = 'trading/dealstat.html'
    model = DealStat
    paginate_by = 100

    date = date.today()  # date(2016, 12, 8)

    def get_queryset(self):
        qs = super(DealStatView, self).get_queryset()
        return qs.filter(time=self.date).select_related('trader')

    def get_day_totals(self):
        return self.get_queryset().aggregate(day_volume=Sum('amount'), day_result=Sum('result_amount'))

    def get_context_data(self, **kwargs):
        context = super(DealStatView, self).get_context_data(**kwargs)
        context.update(self.get_day_totals())
        context.update({
            'date': self.date,
        })
        return context




