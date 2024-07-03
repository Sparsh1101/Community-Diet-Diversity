from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .decorators import *
from .helper_functions import *

@login_required(login_url="accounts:loginlink")
def forbidden(request):
    login = False
    if request.user.get_username() != "":
        login = True
    return render(request, "other/forbidden.html", {"login": login})


@login_required(login_url="accounts:loginlink")
@user_passes_test(
    lambda user: is_parent(user) or is_student(user),
    login_url="accounts:forbidden",
)
def already_filled(request):
    return render(request, "other/already_filled.html", {})


@login_required(login_url="accounts:loginlink")
@user_passes_test(
    lambda user: is_parent(user) or is_student(user),
    login_url="accounts:forbidden",
)
def form_closed(request):
    return render(request, "other/form_closed.html", {})
