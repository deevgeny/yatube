from django.shortcuts import render


def page_not_found(request, exception):
    """Override default handler404."""
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def csrf_failure(request, reason=''):
    """Override default handler403 (csrf failure)."""
    return render(request, 'core/403csrf.html')


def server_error(request):
    """Override default handler500."""
    return render(request, 'core/500.html', status=500)


def permission_denied(request, exception):
    """Overide default handler403."""
    return render(request, 'core/403.html', status=403)
