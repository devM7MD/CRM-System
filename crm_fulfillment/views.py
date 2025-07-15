from django.shortcuts import render

def page_not_found(request, exception):
    """
    404 error handler
    """
    return render(request, '404.html', status=404)

def server_error(request):
    """
    500 error handler
    """
    return render(request, '500.html', status=500)

def permission_denied(request, exception):
    """
    403 error handler
    """
    return render(request, '403.html', status=403)

def bad_request(request, exception):
    """
    400 error handler
    """
    return render(request, '400.html', status=400) 