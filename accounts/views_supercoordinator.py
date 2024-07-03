import io
import xlsxwriter
import os
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required, user_passes_test
from .decorators import *
from .models import *
from .forms import *
from .helper_functions import *
from shared.encryption import EncryptionHelper

encryptionHelper = EncryptionHelper()


@login_required(login_url="accounts:loginlink")
@user_passes_test(is_supercoordinator, login_url="accounts:forbidden")
def supercoordinator_dashboard(request):
    organizations = Organization.objects.all()

    return render(
        request,
        "supercoordinator/supercoordinator_dashboard.html",
        {"organizations": organizations, "page_type": "supercoordinator_dashboard"},
    )


@login_required(login_url="accounts:loginlink")
@user_passes_test(is_supercoordinator, login_url="accounts:forbidden")
def addOrganizationForm(request):
    if request.method == "GET":
        form = OrganizationsInfoForm()
        return render(
            request,
            "supercoordinator/add_organization.html",
            {
                "form": form,
                "valid_state": True,
                "valid_city": True,
                "state": "",
                "city": "",
            },
        )
    else:
        form = OrganizationsInfoForm(request.POST)
        if form.is_valid():
            temp = check_state_city(True, 0, str(request.POST["state"]))
            if temp[0]:
                if not check_state_city(False, temp[1], str(request.POST["city"])):
                    return render(
                        request,
                        "supercoordinator/add_organization.html",
                        {
                            "form": form,
                            "valid_state": True,
                            "valid_city": False,
                            "state": request.POST["state"],
                            "city": request.POST["city"],
                        },
                    )
            else:
                return render(
                    request,
                    "supercoordinator/add_organization.html",
                    {
                        "form": form,
                        "valid_state": False,
                        "valid_city": True,
                        "state": request.POST["state"],
                        "city": request.POST["city"],
                    },
                )
            organization = form.save(commit=False)
            organization.state = State.objects.get(state=request.POST["state"])
            organization.city = City.objects.get(city=request.POST["city"])
            organization.save()
            return redirect("accounts:supercoordinator_dashboard")
        else:
            return render(
                request,
                "supercoordinator/add_organization.html",
                {
                    "form": form,
                    "valid_state": True,
                    "valid_city": True,
                    "state": request.POST["state"],
                    "city": request.POST["city"],
                },
            )


@login_required(login_url="accounts:loginlink")
@user_passes_test(is_supercoordinator, login_url="accounts:forbidden")
def viewCoordinators(request, id):
    organization = Organization.objects.filter(id=id).first()
    coordinators = organization.coordinatorincharge_set.all()
    for coordinator in coordinators:
        coordinator.fname = encryptionHelper.decrypt(coordinator.fname)
        coordinator.lname = encryptionHelper.decrypt(coordinator.lname)
        if coordinator.mobile_no:
            coordinator.mobile_no = encryptionHelper.decrypt(coordinator.mobile_no)
            if coordinator.mobile_no == "":
                coordinator.mobile_no = "-"
        else:
            coordinator.mobile_no = "-"
        if coordinator.email:
            coordinator.email = encryptionHelper.decrypt(coordinator.email)
            if coordinator.email == "":
                coordinator.email = "-"
        else:
            coordinator.email = "-"
    if "my_messages" in request.session:
        my_messages = request.session["my_messages"]
        del request.session["my_messages"]
        return render(
            request,
            "supercoordinator/view_coordinators.html",
            {
                "coordinators": coordinators,
                "organization": organization,
                "my_messages": my_messages,
                "page_type": "view_coordinators",
                "org_id": id,
            },
        )
    else:
        return render(
            request,
            "supercoordinator/view_coordinators.html",
            {
                "coordinators": coordinators,
                "organization": organization,
                "page_type": "view_coordinators",
                "org_id": id,
            },
        )


@login_required(login_url="accounts:loginlink")
@user_passes_test(is_supercoordinator, login_url="accounts:forbidden")
def addCoordinatorForm(request, id):
    if request.method == "GET":
        form = CoordinatorsInfoForm()
        return render(
            request,
            "supercoordinator/add_coordinator.html",
            {"form": form},
        )
    else:
        form = CoordinatorsInfoForm(request.POST)
        if form.is_valid():
            password = random_password_generator()
            coordinatoruser = User.objects.create_user(
                username=username_generator(
                    request.POST["fname"], request.POST["lname"]
                ),
                password=password,
            )
            coordinatoruser.save()
            coordinator_group = Group.objects.get(name="Coordinators")
            coordinatoruser.groups.add(coordinator_group)
            coordinatoruser.save()
            coordinator = form.save(commit=False)
            coordinator.user = coordinatoruser
            coordinator.email = encryptionHelper.encrypt(request.POST["email"])
            coordinator.fname = encryptionHelper.encrypt(request.POST["fname"])
            coordinator.mname = encryptionHelper.encrypt(request.POST["mname"])
            coordinator.lname = encryptionHelper.encrypt(request.POST["lname"])
            coordinator.aadhar = encryptionHelper.encrypt(request.POST["aadhar"])
            coordinator.dob = encryptionHelper.encrypt(request.POST["dob"])
            coordinator.gender = encryptionHelper.encrypt(request.POST["gender"])
            coordinator.mobile_no = encryptionHelper.encrypt(request.POST["mobile_no"])
            coordinator.super_coordinator = SuperCoordinator.objects.filter(
                user=request.user
            ).first()
            coordinator.organization = Organization.objects.filter(id=id).first()
            coordinator.first_password = password
            coordinator.password_changed = False
            coordinator.profile_pic = "accounts/default.svg"
            coordinator.save()
            request.session["my_messages"] = {
                "success": "Registration Successful. Download the Login Credentials from the sidebar on the left."
            }
            return redirect("accounts:view_coordinators", id)
        else:
            return render(
                request,
                "supercoordinator/add_coordinator.html",
                {"form": form},
            )


@login_required(login_url="accounts:loginlink")
@user_passes_test(is_supercoordinator, login_url="accounts:forbidden")
def allCoordinators(request):
    coordinators = CoordinatorInCharge.objects.all()
    for coordinator in coordinators:
        coordinator.fname = encryptionHelper.decrypt(coordinator.fname)
        coordinator.lname = encryptionHelper.decrypt(coordinator.lname)
        if coordinator.mobile_no:
            coordinator.mobile_no = encryptionHelper.decrypt(coordinator.mobile_no)
            if coordinator.mobile_no == "":
                coordinator.mobile_no = "-"
        else:
            coordinator.mobile_no = "-"
        if coordinator.email:
            coordinator.email = encryptionHelper.decrypt(coordinator.email)
            if coordinator.email == "":
                coordinator.email = "-"
        else:
            coordinator.email = "-"
    return render(
        request,
        "supercoordinator/all_coordinators.html",
        {"coordinators": coordinators, "page_type": "all_coordinators"},
    )


@login_required(login_url="accounts:loginlink")
@user_passes_test(is_supercoordinator, login_url="accounts:forbidden")
def supercoordinator_reset_password(request):
    if request.method == "GET":
        form = SuperCoordPasswordReset()
        return render(
            request,
            "supercoordinator/supercoordinator_reset_password.html",
            {"form": form, "page_type": "reset_password"},
        )
    else:
        form = SuperCoordPasswordReset(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                if is_coordinator(user):
                    password = random_password_generator()
                    user_coord = CoordinatorInCharge.objects.get(user=user)
                    user_coord.first_password = password
                    user_coord.password_changed = False
                    user_coord.save()
                    user.set_password(password)
                    user.save()
                    return render(
                        request,
                        "supercoordinator/supercoordinator_reset_password.html",
                        {
                            "form": form,
                            "page_type": "reset_password",
                            "my_messages": {
                                "success": "Password reset successfull. Download login credentions from the sidebar on the left."
                            },
                        },
                    )
                else:
                    return render(
                        request,
                        "supercoordinator/supercoordinator_reset_password.html",
                        {
                            "form": form,
                            "page_type": "reset_password",
                            "my_messages": {
                                "error": "Provided user is not a Coordinator."
                            },
                        },
                    )
            else:
                return render(
                    request,
                    "supercoordinator/supercoordinator_reset_password.html",
                    {
                        "form": form,
                        "page_type": "reset_password",
                        "my_messages": {"error": "Invalid username."},
                    },
                )
        else:
            return render(
                request,
                "supercoordinator/supercoordinator_reset_password.html",
                {"form": form, "page_type": "reset_password"},
            )


@login_required(login_url="accounts:loginlink")
@user_passes_test(is_supercoordinator, login_url="accounts:forbidden")
def coordinators_data_download(request):
    output = io.BytesIO()
    wb = xlsxwriter.Workbook(output)
    bold = wb.add_format({"bold": True})
    merge_format = wb.add_format(
        {
            "bold": True,
            "align": "center",
            "valign": "vcenter",
        }
    )
    credentials = wb.add_worksheet("Coordinators Data")
    credentials.set_row(0, 40)
    credentials.merge_range(
        "A1:K1",
        '"***" indicates password changed by the user. (MAKE SURE THAT THE FOLLOWING SHEET CANNOT BE ACCESSED BY UNAUTHORIZED USERS SINCE IT CONTAINS SENSITIVE DATA)',
        merge_format,
    )
    columns = [
        "USERNAME",
        "PASSWORD",
        "First Name",
        "Middle Name",
        "Last Name",
        "Organization",
        "Aadhar Number",
        "Email",
        "Mobile Number",
        "Date of Birth",
        "Gender",
    ]
    credentials.set_column(0, len(columns) - 1, 18)
    for col_num in range(len(columns)):
        credentials.write(1, col_num, columns[col_num], bold)
    coord = CoordinatorInCharge.objects.filter()
    for row_no, x in enumerate(coord):
        credentials.write(row_no + 2, 0, x.user.username)
        if x.password_changed:
            credentials.write(row_no + 2, 1, "***")
        else:
            credentials.write(row_no + 2, 1, x.first_password)
        credentials.write(row_no + 2, 2, encryptionHelper.decrypt(x.fname))
        if x.mname:
            x.mname = encryptionHelper.decrypt(x.mname)
            if x.mname == "":
                x.mname = "-"
        else:
            x.mname = "-"
        credentials.write(row_no + 2, 3, x.mname)
        credentials.write(row_no + 2, 4, encryptionHelper.decrypt(x.lname))
        credentials.write(row_no + 2, 5, x.organization.name)
        if x.aadhar:
            x.aadhar = encryptionHelper.decrypt(x.aadhar)
            if x.aadhar == "":
                x.aadhar = "-"
        else:
            x.aadhar = "-"
        credentials.write(row_no + 2, 6, x.aadhar)
        if x.email:
            x.email = encryptionHelper.decrypt(x.email)
            if x.email == "":
                x.email = "-"
        else:
            x.email = "-"
        credentials.write(row_no + 2, 7, x.email)
        if x.mobile_no:
            x.mobile_no = encryptionHelper.decrypt(x.mobile_no)
            if x.mobile_no == "":
                x.mobile_no = "-"
        else:
            x.mobile_no = "-"
        credentials.write(row_no + 2, 8, x.mobile_no)
        dob = encryptionHelper.decrypt(x.dob).split("/")
        dob[1], dob[0] = dob[0], dob[1]
        dob = "/".join(dob)
        credentials.write(row_no + 2, 9, dob)
        credentials.write(row_no + 2, 10, encryptionHelper.decrypt(x.gender))
    wb.close()
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = "attachment; filename=Coordinators Data.xlsx"
    return response


@login_required(login_url="accounts:loginlink")
@user_passes_test(
    lambda user: is_supercoordinator(user),
    login_url="accounts:forbidden",
)
def view_supercoordinator_profile(request):
    if request.method == "GET":
        user = request.user
        if is_supercoordinator(user):
            supercoordinator = SuperCoordinator.objects.filter(user=user).first()

            supercoordinator.fname = encryptionHelper.decrypt(supercoordinator.fname)
            supercoordinator.lname = encryptionHelper.decrypt(supercoordinator.lname)

            if supercoordinator.mname:
                supercoordinator.mname = encryptionHelper.decrypt(
                    supercoordinator.mname
                )
                if supercoordinator.mname == "":
                    supercoordinator.mname = ""
            else:
                supercoordinator.mname = ""

            if supercoordinator.aadhar:
                supercoordinator.aadhar = encryptionHelper.decrypt(
                    supercoordinator.aadhar
                )
                if supercoordinator.aadhar == "":
                    supercoordinator.aadhar = "-"
            else:
                supercoordinator.aadhar = "-"

            if supercoordinator.email:
                supercoordinator.email = encryptionHelper.decrypt(
                    supercoordinator.email
                )
                if supercoordinator.email == "":
                    supercoordinator.email = "-"
            else:
                supercoordinator.email = "-"

            if supercoordinator.mobile_no:
                supercoordinator.mobile_no = encryptionHelper.decrypt(
                    supercoordinator.mobile_no
                )
                if supercoordinator.mobile_no == "":
                    supercoordinator.mobile_no = "-"
            else:
                supercoordinator.mobile_no = "-"

            supercoordinator.dob = encryptionHelper.decrypt(supercoordinator.dob)
            supercoordinator.gender = encryptionHelper.decrypt(supercoordinator.gender)

            return render(
                request,
                "supercoordinator/view_supercoordinator_profile.html",
                {
                    "page_type": "view_supercoordinator_profile",
                    "supercoordinator": supercoordinator,
                },
            )


@login_required(login_url="accounts:loginlink")
@user_passes_test(
    lambda user: is_supercoordinator(user),
    login_url="accounts:forbidden",
)
def edit_supercoordinator_profile(request):
    supercoordinator = SuperCoordinator.objects.filter(user=request.user).first()
    if request.method == "GET":
        initial_dict = {
            "fname": encryptionHelper.decrypt(supercoordinator.fname),
            "lname": encryptionHelper.decrypt(supercoordinator.lname),
            "profile_pic": supercoordinator.profile_pic,
            "dob": encryptionHelper.decrypt(supercoordinator.dob),
            "gender": encryptionHelper.decrypt(supercoordinator.gender),
        }

        if supercoordinator.mname:
            initial_dict["mname"] = encryptionHelper.decrypt(supercoordinator.mname)
        if supercoordinator.aadhar:
            initial_dict["aadhar"] = encryptionHelper.decrypt(supercoordinator.aadhar)
        if supercoordinator.email:
            initial_dict["email"] = encryptionHelper.decrypt(supercoordinator.email)
        if supercoordinator.mobile_no:
            initial_dict["mobile_no"] = encryptionHelper.decrypt(
                supercoordinator.mobile_no
            )

        form = SuperCoordinatorsInfoForm(request.POST or None, initial=initial_dict)
        form.fields["dob"].disabled = True

        return render(
            request,
            "supercoordinator/update_supercoordinators_info.html",
            {"form": form},
        )
    else:
        form = SuperCoordinatorsInfoForm(request.POST, request.FILES)
        form.fields["dob"].disabled = True
        form.fields["dob"].initial = encryptionHelper.decrypt(supercoordinator.dob)

        if form.is_valid():
            supercoordinator = SuperCoordinator.objects.filter(
                user=request.user
            ).first()

            if supercoordinator.mname:
                supercoordinator.mname = encryptionHelper.encrypt(request.POST["mname"])
            if supercoordinator.aadhar:
                supercoordinator.aadhar = encryptionHelper.encrypt(
                    request.POST["aadhar"]
                )
            if supercoordinator.email:
                supercoordinator.email = encryptionHelper.encrypt(request.POST["email"])
            if supercoordinator.mobile_no:
                supercoordinator.mobile_no = encryptionHelper.encrypt(
                    request.POST["mobile_no"]
                )

            supercoordinator.fname = encryptionHelper.encrypt(request.POST["fname"])
            supercoordinator.lname = encryptionHelper.encrypt(request.POST["lname"])
            supercoordinator.gender = encryptionHelper.encrypt(request.POST["gender"])

            if request.FILES:
                if request.FILES["profile_pic"].size > 5 * 1024 * 1024:
                    form.add_error("profile_pic", "File size must be less than 5MB.")

                    return render(
                        request,
                        "supercoordinator/update_supercoordinators_info.html",
                        {
                            "form": form,
                        },
                    )
                else:
                    x = supercoordinator.profile_pic.url.split("/media/accounts/")
                    if x[1] != "default.svg":
                        file = settings.MEDIA_ROOT + "/accounts/" + x[1]
                        os.remove(file)
                    supercoordinator.profile_pic = request.FILES["profile_pic"]
            else:
                if "profile_pic-clear" in request.POST.keys():
                    x = supercoordinator.profile_pic.url.split("/media/accounts/")
                    if x[1] != "default.svg":
                        file = settings.MEDIA_ROOT + "/accounts/" + x[1]
                        os.remove(file)
                    supercoordinator.profile_pic = "accounts/default.svg"

            supercoordinator.save()
            return redirect("accounts:view_supercoordinator_profile")
        else:
            return render(
                request,
                "supercoordinator/update_supercoordinators_info.html",
                {"form": form},
            )


@login_required(login_url="accounts:loginlink")
@user_passes_test(is_supercoordinator, login_url="accounts:forbidden")
@password_change_required
def switchCoordinatorsList(request, coord_id, page_id):
    og_coordinator = CoordinatorInCharge.objects.filter(id=coord_id).first()
    og_coordinator_user = og_coordinator.user
    organization = og_coordinator.organization
    if request.method == "GET":
        coordinators = organization.coordinatorincharge_set.all()
        coordinators_without_og = []

        for coordinator in coordinators:
            if coordinator != og_coordinator:
                coordinators_without_og.append(coordinator)

        for coordinator in coordinators_without_og:
            coordinator.fname = encryptionHelper.decrypt(coordinator.fname)
            coordinator.lname = encryptionHelper.decrypt(coordinator.lname)
        return render(
            request,
            "supercoordinator/switch_coordinators_list.html",
            {
                "page_type": "switch_coordinators_list",
                "coordinators": coordinators_without_og,
            },
        )
    else:
        new_coordinator_id = request.POST.get("new_coordinator")
        new_coordinator = CoordinatorInCharge.objects.filter(
            id=new_coordinator_id
        ).first()
        sessions = Session.objects.filter(coordinator=og_coordinator)
        teachers = TeacherInCharge.objects.filter(coordinator=og_coordinator)
        for session in sessions:
            session.coordinator = new_coordinator
            session.save()

        for teacher in teachers:
            teacher.coordinator = new_coordinator
            teacher.save()

        og_coordinator_user.delete()

        if page_id == 1:
            return redirect("accounts:view_coordinators", organization.id)
        elif page_id == 2:
            return redirect("accounts:all_coordinators")


@login_required(login_url="accounts:loginlink")
@user_passes_test(is_supercoordinator, login_url="accounts:forbidden")
@password_change_required
def removeCoordinator(request, coord_id, page_id):
    coordinator = CoordinatorInCharge.objects.filter(id=coord_id).first()
    coordinator_user = coordinator.user
    organization = coordinator.organization
    sessions = Session.objects.filter(coordinator=coordinator)
    teachers = TeacherInCharge.objects.filter(coordinator=coordinator)
    teachers_user = []
    for teacher in teachers:
        teachers_user.append(teacher.user)
    for session in sessions:
        for teacher in teachers:
            students = StudentsInfo.objects.filter(session=session, teacher=teacher)
            for student in students:
                student.teacher = None
                student.session = None
                student.save()
            Teacher_Session.objects.filter(teacher=teacher).delete()
            Student_Session.objects.filter(session=session, teacher=teacher).delete()
    sessions.delete()
    for teacher in teachers_user:
        teacher.delete()
    coordinator_user.delete()
    request.session["my_messages"] = {"success": "Coordinator deleted successfully"}
    if page_id == 1:
        return redirect("accounts:view_coordinators", organization.id)
    elif page_id == 2:
        return redirect("accounts:all_coordinators")
