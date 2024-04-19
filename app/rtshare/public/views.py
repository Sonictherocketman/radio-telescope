from django.shortcuts import render

from telescope.models import Telescope


def home_view(request):
    return render(request, 'home.html', context={
        'telescopes': Telescope.objects.filter(status=Telescope.Status.ACTIVE)
    })
