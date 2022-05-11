from datetime import date


def year(request):
    """Return year {'year': YYYY}."""
    return {
        'year': date.today().year
    }
