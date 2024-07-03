from .models import *
from django.shortcuts import redirect
from django.contrib.auth import logout
from .helper_functions import *


def isActive(moduleType, userType):
    def decorator(view_func):
        def wrap(request, *args, **kwargs):
            module = Form.objects.get(name=moduleType)
            if not "parent_dashboard" in request.build_absolute_uri().split("/"):
                if request.user.groups.filter(name="Parents").exists():
                    return redirect("accounts:forbidden")
                student = StudentsInfo.objects.get(user=request.user)
                if FormDetails.objects.filter(
                    form=module, open=True, teacher=student.teacher
                ).exists():
                    return view_func(request, *args, **kwargs)
                else:
                    return redirect("accounts:form_closed")

            elif "parent_dashboard" in request.build_absolute_uri().split("/"):
                studentID = request.META.get("HTTP_REFERER").split("/")[-2]
                student = (
                    ParentsInfo.objects.filter(user=request.user)
                    .first()
                    .studentsinfo_set.get(pk=studentID)
                )
                if FormDetails.objects.filter(
                    form=module, open=True, teacher=student.teacher
                ).exists():
                    return view_func(request, *args, **kwargs)
                else:
                    return redirect("accounts:form_closed")

        return wrap

    return decorator


def isInfoActive(moduleType):
    def decorator(view_func):
        def wrap(request, *args, **kwargs):
            module = Form.objects.get(name=moduleType)
            if not "parent_dashboard" in request.build_absolute_uri().split("/"):
                if request.user.groups.filter(name="Parents").exists():
                    return redirect("accounts:forbidden")
                if InfoFormDetails.objects.filter(
                    form=module,
                    open=True,
                ).exists():
                    return view_func(request, *args, **kwargs)
                else:
                    return redirect("accounts:form_closed")

            elif "parent_dashboard" in request.build_absolute_uri().split("/"):
                if InfoFormDetails.objects.filter(
                    form=module,
                    open=True,
                ).exists():
                    return view_func(request, *args, **kwargs)
                else:
                    return redirect("accounts:form_closed")

        return wrap

    return decorator


def redirect_to_dashboard(func):
    def logic(request, *args, **kwargs):
        def my_redirect(request):
            if is_teacher(request.user):
                return redirect("accounts:teacher_all_sessions")
            elif is_parent(request.user):
                return redirect("accounts:parent_dashboard")
            elif is_student(request.user):
                return redirect("accounts:student_dashboard")
            elif is_coordinator(request.user):
                return redirect("accounts:coordinator_dashboard")
            elif is_supercoordinator(request.user):
                return redirect("accounts:supercoordinator_dashboard")
            else:
                logout(request)
                return redirect("accounts:loginlink")

        if request.user.get_username() != "":
            return my_redirect(request)
        else:
            return func(request, *args, **kwargs)

    return logic


def registration_data_cleanup(func):
    def logic(request, *args, **kwargs):
        if "consent_data" in request.session:
            del request.session["consent_data"]
        if "data" in request.session:
            del request.session["data"]
        if "dob" in request.session:
            del request.session["dob"]
        if "registration_visited" in request.session:
            del request.session["registration_visited"]
        if "consent_visited" in request.session:
            del request.session["consent_visited"]
        if "parents_info_visited" in request.session:
            del request.session["parents_info_visited"]
        if "forgot_password" in request.session:
            del request.session["forgot_password"]
        return func(request, *args, **kwargs)

    return logic


def password_change_required(func):
    def logic(request, *args, **kwargs):
        user = request.user
        if is_coordinator(user):
            coord = CoordinatorInCharge.objects.get(user=user)
            if not coord.password_changed:
                return redirect("accounts:change_password")
        elif is_teacher(user):
            teacher = TeacherInCharge.objects.get(user=user)
            if not teacher.password_changed:
                return redirect("accounts:change_password")
        elif is_parent(user):
            parent = ParentsInfo.objects.get(user=user)
            if not parent.password_changed:
                return redirect("accounts:change_password")
        elif is_student(user):
            student = StudentsInfo.objects.get(user=user)
            if not student.password_changed:
                return redirect("accounts:change_password")
        return func(request, *args, **kwargs)

    return logic


def secondary_reg(func):
    def logic(request, *args, **kwargs):
        if is_student(request.user):
            student = StudentsInfo.objects.filter(user=request.user).first()
            secondary_reg_fields = student.secondary_reg
            if secondary_reg_fields == None:
                return redirect("accounts:secondary_registration")
            else:
                secondary_reg_fields_names = [
                    f.name for f in secondary_reg_fields._meta.get_fields()
                ][2:]
                for i in secondary_reg_fields_names:
                    if getattr(secondary_reg_fields, i) == None:
                        return redirect("accounts:secondary_registration")
        return func(request, *args, **kwargs)

    return logic


def consent(func):
    def logic(request, *args, **kwargs):
        if is_student(request.user):
            student = StudentsInfo.objects.filter(user=request.user).first()
            if not student.consent:
                if is_adult_student(request.user):
                    return redirect("accounts:give_consent")
                else:
                    if student.parent.consent:
                        student.consent = True
                        student.save()
                    else:
                        return redirect("accounts:ask_to_give_consent")
        elif is_parent(request.user):
            parent = ParentsInfo.objects.filter(user=request.user).first()
            if not parent.consent:
                return redirect("accounts:give_consent")
        return func(request, *args, **kwargs)

    return logic
