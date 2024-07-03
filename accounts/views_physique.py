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


def creatingOrUpdatingDraftsPhysique(temp, user, formName):
    student = StudentsInfo.objects.get(user=user)
    startdate = InfoFormDetails.objects.get(
        form=Form.objects.get(name=formName),
        open=True,
    ).start_timestamp
    if Physique.objects.filter(
        student=student, submission_timestamp__gte=startdate
    ).exists():
        draftForm = Physique.objects.get(
            student=StudentsInfo.objects.get(user=user),
            submission_timestamp__gte=startdate,
        )
        if draftForm.draft:
            # updating drafts
            for name in Physique._meta.get_fields():
                name = name.column
                if name == "id" or name == "student_id" or name == "draft":
                    continue
                if name in temp:
                    setattr(draftForm, name, temp[name])
                else:
                    setattr(draftForm, name, getattr(draftForm, name) or None)

            draftForm.submission_timestamp = datetime.now()
            if draftForm.waist == "":
                draftForm.waist = 0
            if draftForm.weight == "":
                draftForm.weight = 0
            if draftForm.hip == "":
                draftForm.hip = 0
            if draftForm.height == "":
                draftForm.height = 0
            draftForm.save()
            return True
    else:
        return False


@login_required(login_url="accounts:loginlink")
@user_passes_test(
    lambda user: is_parent(user) or is_student(user), login_url="accounts:forbidden"
)
@consent
@password_change_required
@secondary_reg
def physiqueDraft(request):
    if "parent_dashboard" in request.META.get("HTTP_REFERER").split("/"):
        student_id = request.META.get("HTTP_REFERER").split("/")[-2]
        user = StudentsInfo.objects.get(pk=student_id).user
    else:
        user = request.user
    # for removing csrf field
    temp = createTempDict(request.POST)
    # checking if draft exists
    if not creatingOrUpdatingDraftsPhysique(temp, user, "physique"):
        # creating new record
        form = Physique(**temp)
        form.student = StudentsInfo.objects.get(user=user)
        form.draft = True
        form.submission_timestamp = datetime.now()
        if form.waist == "":
            form.waist = 0
        if form.weight == "":
            form.weight = 0
        if form.hip == "":
            form.hip = 0
        if form.height == "":
            form.height = 0
        form.save()
    return redirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="accounts:loginlink")
@user_passes_test(
    lambda user: is_parent(user) or is_student(user), login_url="accounts:forbidden"
)
@consent
@password_change_required
@secondary_reg
@isInfoActive("physique")
def physique(request, user=None):
    if request.method == "GET":
        if user == None:
            user = request.user

        student = StudentsInfo.objects.get(user=user)
        if student.session != None:
            startdate = InfoFormDetails.objects.get(
                form=Form.objects.get(name="physique"), open=True
            ).start_timestamp
            if Physique.objects.filter(
                student=student, submission_timestamp__gte=startdate
            ).exists():
                draftForm = Physique.objects.get(
                    student=StudentsInfo.objects.get(user=user),
                    submission_timestamp__gte=startdate,
                )
                if draftForm.draft:
                    mod = PhysiqueForm()
                    temp = {}
                    for name in Physique._meta.get_fields():
                        name = name.column
                        if name in mod.fields:
                            temp[name] = getattr(draftForm, name) or None
                    form = PhysiqueForm(temp)
                    return render(
                        request,
                        "physique/physique.html",
                        {"form": form, "page_type": "student_physique"},
                    )
                else:
                    return redirect("accounts:already_filled")
            # new form
            else:
                form = PhysiqueForm()
                return render(
                    request,
                    "physique/physique.html",
                    {"form": form, "page_type": "student_physique"},
                )
        else:
            return redirect("accounts:forbidden")

    # POST
    else:
        flag = False
        if user == None:
            flag = True
            user = request.user
        form = PhysiqueForm(request.POST)

        # valid form
        if form.is_valid():
            temp = createTempDict(request.POST)
            startdate = InfoFormDetails.objects.get(
                form=Form.objects.get(name="physique"),
                open=True,
            ).start_timestamp
            physiqueDraft(request)
            draftForm = Physique.objects.get(
                student=StudentsInfo.objects.get(user=user),
                submission_timestamp__gte=startdate,
            )
            if draftForm.draft:
                for name in Physique._meta.get_fields():
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
            return render(
                request,
                "physique/physique.html",
                {"form": form, "page_type": "student_physique"},
            )


@login_required(login_url="accounts:loginlink")
@user_passes_test(is_parent, login_url="accounts:forbidden")
@consent
@password_change_required
@isInfoActive("physique")
def parentPhysique(request, id):
    user = StudentsInfo.objects.get(pk=id).user
    return physique(request, user)
