from django.shortcuts import redirect

def redirect_to_home(request):
    """
    Simple view to redirect to the home page
    """
    return redirect('authentication:home')