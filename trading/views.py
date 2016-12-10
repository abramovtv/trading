from django.http import HttpResponse
from django.views.generic import TemplateView

def index(request):
    return HttpResponse("Trading index.")

class AdminStatView(TemplateView):
    template_name = 'stats.html'


