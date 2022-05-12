from http import HTTPStatus

from django.shortcuts import render


def page_not_found(request, exception):
    """Override default handler404."""
    return render(
        request, 'core/404.html',
        {'path': request.path}, status=HTTPStatus.NOT_FOUND.value
    )


def csrf_failure(request, reason=''):
    """Override default handler403 (csrf failure)."""
    return render(request, 'core/403csrf.html')


def server_error(request):
    """Override default handler500."""
    return render(
        request, 'core/500.html',
        status=HTTPStatus.INTERNAL_SERVER_ERROR.value
    )


def permission_denied(request, exception):
    """Overide default handler403."""
    return render(
        request, 'core/403.html',
        status=HTTPStatus.FORBIDDEN.value)
