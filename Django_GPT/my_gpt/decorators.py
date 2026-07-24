from functools import wraps
from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import redirect


def model_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)

        query_string = urlencode(
            {
                "next": request.get_full_path(),
                "required": "1",
            }
        )

        return redirect(
            f"{settings.LOGIN_URL}?{query_string}"
        )

    return wrapper