from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request,'home.html')
def loging(request):
    return render(request,'loging.html')
def singup(request):
    return render(request,'singup.html')
def services(request):
    return render(request,'services.html')
def about(request):
    return render(request,'about.html')
def tasker(request):
    return render(request,'tasker.html')
