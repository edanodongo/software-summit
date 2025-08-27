from django.shortcuts import render

# Create your views here.


# View for event page
def landingEvent(request):
    return render(request, 'landingpage/index.html')