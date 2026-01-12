
# Project-wide utils.py

import functools
from django.shortcuts import render
from django.http import HttpRequest, HttpResponseBadRequest, HttpResponseForbidden


def safe_method_validator(backup_render_template_path, safe_methods_list):
    """
    Docstring for safe_method_validator
    
    :param template: The path to the template this view should re-route to if 
    this view is called from any request method besides the intended method.
    
    Example Usage:
    @safe_method_validator(".\\path\\to\\backup\\template.html", ["GET", "HEAD", "OPTIONS"])
    def my_get_method_view_function(request, _context):
        pass
    """
    def outer(view_func):
        @functools.wraps(view_func)
        def wrapper(request: HttpRequest, _context, *args, **kwargs):
            if request.method not in safe_methods_list:
                return render(request=request, template_name=backup_render_template_path, context=_context)
            elif(not request.user.is_authenticated):
                return HttpResponseForbidden("This requires an authenticated user -> Blocked by: `accounts` views.py -> safe_method_validator()")
            elif(request.method in safe_methods_list):
                return view_func(request, _context, *args, **kwargs)
            else:
                safe_methods = lambda a: ', '.join(a for a in safe_methods_list)
                return HttpResponseBadRequest(f"Method {request.method} is not in list of safe_methods for this view function. Safe methods include [{safe_methods}]")
            return view_func
        return wrapper
    return outer


