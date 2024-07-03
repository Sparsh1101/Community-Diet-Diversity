import ast
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .decorators import *
from .models import *
from .forms import *
from .helper_functions import *


def createTempDict(postData):
    temp = {}
    for key in postData:
        if key == "source_fruits_vegetables" or key == "grow_own_food":
            temp[key] = postData.getlist(key)
        else:
            temp[key] = postData[key]
    del temp["csrfmiddlewaretoken"]
    return temp


def creatingOrUpdatingDrafts(temp, user, formName):
    student = StudentsInfo.objects.get(user=user)
    try:
        startdate = FormDetails.objects.get(
            form=Form.objects.get(name=formName), teacher=student.teacher, open=True, session=student.session
        ).start_timestamp
        if ModuleOne.objects.filter(
            student=student, submission_timestamp__gte=startdate
        ).exists():
            draftForm = ModuleOne.objects.get(
                student=StudentsInfo.objects.get(user=user),
                submission_timestamp__gte=startdate,
            )
            if draftForm.draft:
                # updating drafts
                for name in ModuleOne._meta.get_fields():
                    name = name.column
                    if name == "id" or name == "student_id" or name == "draft":
                        continue
                    if name in temp:
                        setattr(draftForm, name, temp[name])
                    else:
                        setattr(draftForm, name, getattr(draftForm, name) or None)

                draftForm.submission_timestamp = datetime.now()
                draftForm.save()
                return True
        else:
            return False
    except:
        return False


@login_required(login_url="accounts:loginlink")
@user_passes_test(
    lambda user: is_parent(user) or is_student(user), login_url="accounts:forbidden"
)
@consent
@password_change_required
@secondary_reg
def draft(request):
    if "parent_dashboard" in request.META.get("HTTP_REFERER").split("/"):
        module = request.META.get("HTTP_REFERER").split("/")[-1]
        id = request.META.get("HTTP_REFERER").split("/")[-2]
        user = StudentsInfo.objects.get(pk=id).user
    else:
        module = request.META.get("HTTP_REFERER").split("/")[-2]
        user = request.user

    # 1st Page
    if module == "moduleOne":
        # for removing csrf field
        temp = createTempDict(request.POST)
        # checking if draft exists
        if not creatingOrUpdatingDrafts(temp, user, "moduleOne"):
            # creating new record
            form = ModuleOne(**temp)
            form.student = StudentsInfo.objects.get(user=user)
            form.draft = True
            formType = getFormType(
                "moduleOne", StudentsInfo.objects.get(user=user).teacher
            )
            form.pre = 1 if formType == "PreTest" else 0
            form.submission_timestamp = datetime.now()
            form.save()
    # 2nd and 3rd Page
    elif module == "moduleOne-2" or module == "moduleOne-3":
        temp = createTempDict(request.POST)
        creatingOrUpdatingDrafts(temp, user, "moduleOne")
    return redirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:loginlink")
@user_passes_test(
    lambda user: is_parent(user) or is_student(user), login_url="accounts:forbidden"
)
@consent
@password_change_required
@secondary_reg
def previous(request):
    link = request.META.get("HTTP_REFERER").split("/")
    if "parent_dashboard" in link:
        if link[-1] == "moduleOne-2":
            link[-1] = "moduleOne"
        elif link[-1] == "moduleOne-3":
            link[-1] = "moduleOne-2"
    else:
        if link[-2] == "moduleOne-2":
            link[-2] = "moduleOne"
        elif link[-2] == "moduleOne-3":
            link[-2] = "moduleOne-2"
    newLink = "/".join(link)
    return redirect(newLink)


@login_required(login_url="accounts:loginlink")
@user_passes_test(
    lambda user: is_parent(user) or is_student(user), login_url="accounts:forbidden"
)
@consent
@password_change_required
@secondary_reg
@isActive("moduleOne", "student")
def moduleOne(request, user=None):
    if request.method == "GET":
        if user == None:
            user = request.user

        student = StudentsInfo.objects.get(user=user)
        try:
            startdate = FormDetails.objects.get(
                form=Form.objects.get(name="moduleOne"), teacher=student.teacher, open=True, session=student.session
            ).start_timestamp
            if ModuleOne.objects.filter(
                student=student, submission_timestamp__gte=startdate
            ).exists():
                draftForm = ModuleOne.objects.get(
                    student=StudentsInfo.objects.get(user=user),
                    submission_timestamp__gte=startdate,
                )
                if draftForm.draft:
                    mod = ModuleOneForm()
                    temp = {}
                    for name in ModuleOne._meta.get_fields():
                        name = name.column
                        if name in mod.fields:
                            if (
                                name == "source_fruits_vegetables"
                                or name == "grow_own_food"
                            ):
                                temp[name] = ast.literal_eval(
                                    getattr(draftForm, name) or "[]"
                                )
                            else:
                                temp[name] = getattr(draftForm, name)

                    form = ModuleOneForm(temp)
                    formPre = getFormType("moduleOne", student.teacher)
                    return render(
                        request,
                        "moduleOne/module_one.html",
                        {
                            "form": form,
                            "formPre": formPre,
                            "page_type": "student_module_one",
                        },
                    )
                else:
                    return redirect("accounts:already_filled")

            # new form
            else:
                form = ModuleOneForm()
                formPre = getFormType("moduleOne", student.teacher)
                return render(
                    request,
                    "moduleOne/module_one.html",
                    {"form": form, "formPre": formPre, "page_type": "student_module_one"},
                )
        except:
            return redirect("accounts:form_closed")

    # POST
    else:

        flag = False
        if user == None:
            flag = True
            user = request.user
        form = ModuleOneForm(request.POST)

        if form.is_valid():
            temp = createTempDict(request.POST)

            if not creatingOrUpdatingDrafts(temp, user, "moduleOne"):
                # creating new record
                form = ModuleOne(**temp)
                form.student = StudentsInfo.objects.get(user=user)
                form.draft = True
                formType = getFormType(
                    "moduleOne", StudentsInfo.objects.get(user=user).teacher
                )
                form.pre = 1 if formType == "PreTest" else 0
                form.submission_timestamp = datetime.now()
                form.save()

            if flag:
                return redirect("accounts:module_one_2")
            else:
                return redirect(
                    "accounts:parentsModuleOne2",
                    id=StudentsInfo.objects.get(user=user).id,
                )

        else:
            formPre = getFormType(
                "moduleOne", StudentsInfo.objects.get(user=user).teacher
            )
            return render(
                request,
                "moduleOne/module_one.html",
                {"form": form, "formPre": formPre, "page_type": "student_module_one"},
            )


@login_required(login_url="accounts:loginlink")
@user_passes_test(
    lambda user: is_parent(user) or is_student(user), login_url="accounts:forbidden"
)
@consent
@password_change_required
@secondary_reg
@isActive("moduleOne", "student")
def moduleOne2(request, user=None):
    if request.method == "GET":
        if user == None:
            user = request.user

        student = StudentsInfo.objects.get(user=user)
        try:
            startdate = FormDetails.objects.get(
                form=Form.objects.get(name="moduleOne"), teacher=student.teacher, open=True, session=student.session
            ).start_timestamp
            if ModuleOne.objects.filter(
                student=student, submission_timestamp__gte=startdate
            ).exists():
                draftForm = ModuleOne.objects.get(
                    student=StudentsInfo.objects.get(user=user),
                    submission_timestamp__gte=startdate,
                )
                if draftForm.draft:
                    mod = ModuleOneForm2()
                    temp = {}
                    for name in ModuleOne._meta.get_fields():
                        name = name.column
                        if name in mod.fields:
                            temp[name] = getattr(draftForm, name) or None

                    form = ModuleOneForm2(temp)
                    formPre = getFormType("moduleOne", student.teacher)
                    return render(
                        request,
                        "moduleOne/module_one2.html",
                        {
                            "form": form,
                            "formPre": formPre,
                            "page_type": "student_module_one",
                        },
                    )
                else:
                    return redirect("accounts:already_filled")

            # new form
            else:
                form = ModuleOneForm2()
                formPre = getFormType("moduleOne", student.teacher)
                return render(
                    request,
                    "moduleOne/module_one2.html",
                    {"form": form, "formPre": formPre, "page_type": "student_module_one"},
                )
        except:
            return redirect("accounts:form_closed")

    # POST
    else:
        flag = False
        if user == None:
            flag = True
            user = request.user
        form = ModuleOneForm2(request.POST)

        if form.is_valid():
            temp = createTempDict(request.POST)
            creatingOrUpdatingDrafts(temp, user, "moduleOne")

            if flag:
                return redirect("accounts:module_one_3")
            else:
                return redirect(
                    "accounts:parentsModuleOne3",
                    id=StudentsInfo.objects.get(user=user).id,
                )
        else:
            formPre = getFormType(
                "moduleOne", StudentsInfo.objects.get(user=user).teacher
            )
            return render(
                request,
                "moduleOne/module_one2.html",
                {"form": form, "formPre": "formPre", "page_type": "student_module_one"},
            )


@login_required(login_url="accounts:loginlink")
@user_passes_test(
    lambda user: is_parent(user) or is_student(user), login_url="accounts:forbidden"
)
@consent
@password_change_required
@secondary_reg
@isActive("moduleOne", "student")
def moduleOne3(request, user=None):
    if request.method == "GET":
        if user == None:
            user = request.user

        student = StudentsInfo.objects.get(user=user)
        try:
            startdate = FormDetails.objects.get(
                form=Form.objects.get(name="moduleOne"), teacher=student.teacher, open=True, session=student.session
            ).start_timestamp
            if ModuleOne.objects.filter(
                student=student, submission_timestamp__gte=startdate
            ).exists():
                draftForm = ModuleOne.objects.get(
                    student=StudentsInfo.objects.get(user=user),
                    submission_timestamp__gte=startdate,
                )
                if draftForm.draft:
                    mod = ModuleOneForm3()
                    temp = {}
                    for name in ModuleOne._meta.get_fields():
                        name = name.column
                        if name in mod.fields:
                            temp[name] = getattr(draftForm, name) or None
                    form = ModuleOneForm3(temp)
                    formPre = getFormType("moduleOne", student.teacher)
                    return render(
                        request,
                        "moduleOne/module_one3.html",
                        {
                            "form": form,
                            "formPre": formPre,
                            "page_type": "student_module_one",
                        },
                    )
                else:
                    return redirect("accounts:already_filled")
            # new form
            else:
                form = ModuleOneForm3()
                formPre = getFormType("moduleOne", student.teacher)
                return render(
                    request,
                    "moduleOne/module_one3.html",
                    {"form": form, "formPre": formPre, "page_type": "student_module_one"},
                )
        except:
            return redirect("accounts:form_closed")
    # POST
    else:
        flag = False
        if user == None:
            flag = True
            user = request.user
        form = ModuleOneForm3(request.POST)

        # valid form
        if form.is_valid():
            temp = createTempDict(request.POST)
            student = StudentsInfo.objects.get(user=user)
            startdate = FormDetails.objects.get(
                form=Form.objects.get(name="moduleOne"),
                teacher=student.teacher,
                open=True,
                session=student.session
            ).start_timestamp
            draftForm = ModuleOne.objects.get(
                student=StudentsInfo.objects.get(user=user),
                submission_timestamp__gte=startdate,
            )
            if draftForm.draft:
                for name in ModuleOne._meta.get_fields():
                    name = name.column
                    if name == "id" or name == "student_id" or name == "draft":
                        continue
                    elif name == "source_fruits_vegetables" or name == "grow_own_food":
                        my_list = "; ".join(ast.literal_eval(getattr(draftForm, name)))
                        setattr(draftForm, name, my_list)
                    elif name in temp:
                        setattr(draftForm, name, temp[name])

                draftForm.draft = False
                draftForm.submission_timestamp = datetime.now()
                draftForm.save()
                if flag:
                    return redirect("accounts:student_dashboard")
                else:
                    return redirect("accounts:parent_dashboard")
        # invalid form
        else:
            formPre = getFormType(
                "moduleOne", StudentsInfo.objects.get(user=user).teacher
            )
            return render(
                request,
                "moduleOne/module_one3.html",
                {"form": form, "formPre": formPre, "page_type": "student_module_one"},
            )


@login_required(login_url="accounts:loginlink")
@user_passes_test(is_parent, login_url="accounts:forbidden")
@consent
@password_change_required
@isActive("moduleOne", "parent")
def parentModuleOne(request, id):
    user = StudentsInfo.objects.get(pk=id).user
    return moduleOne(request, user)


@login_required(login_url="accounts:loginlink")
@user_passes_test(is_parent, login_url="accounts:forbidden")
@consent
@password_change_required
@isActive("moduleOne", "parent")
def parentModuleOne2(request, id):
    user = StudentsInfo.objects.get(pk=id).user
    return moduleOne2(request, user)


@login_required(login_url="accounts:loginlink")
@user_passes_test(is_parent, login_url="accounts:forbidden")
@consent
@password_change_required
@isActive("moduleOne", "parent")
def parentModuleOne3(request, id):
    user = StudentsInfo.objects.get(pk=id).user
    return moduleOne3(request, user)
