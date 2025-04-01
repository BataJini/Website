from django.shortcuts import redirect
from django.shortcuts import render

def redirect_to_home(request):
    """
    Simple view to redirect to the home page
    """
    return redirect('authentication:home')

def custom_404(request, exception=None):
    """
    Custom 404 view that can be called both as a view and as an error handler
    """
    return render(request, '404.html', {'message': 'Page not found'}, status=404)