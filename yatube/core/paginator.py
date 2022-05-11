from django.core.paginator import Paginator


def get_page_object(request, queryset, limit):
    """Get page object function.

    Required arguments: request (HttpRequest), queryset (QuerySet),
    limit (Integer).
    Return paginator page object from queryset using page number
    from request and limit (number of items to display per page)
    """
    paginator = Paginator(queryset, limit)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
