from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required, user_passes_test
from .decorators import *
from .models import *
from .forms import *
from .helper_functions import *
from shared.encryption import EncryptionHelper

encryptionHelper = EncryptionHelper()


def root(request):
    return redirect("accounts:loginlink")


@registration_data_cleanup
@redirect_to_dashboard
def loginU(request):
    if request.method == "GET":
        form = CustomAuthenticationForm()
        return render(request, "registration/login.html", {"form": form})
    else:
        form = CustomAuthenticationForm(request.POST)
        username = request.POST["username"]
        password = request.POST["password"]
        grp = request.POST["groups"]
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            if user.check_password(password):
                our_user = custom_user_filter(user)
                if our_user == None:
                    return render(
                        request,
                        "registration/login.html",
                        {"form": form, "my_messages": {"error": "Access Denied."}},
                    )
                else:
                    grp_name = our_user[1]
                    grp = Group.objects.get(pk=grp).name
                    if grp_name == grp:
                        user_authenticated = authenticate(
                            request, username=username, password=password
                        )
                        request.session.set_expiry(86400)
                        login(request, user_authenticated)
                        if grp_name == "Parents":
                            return redirect("accounts:parent_dashboard")
                        elif grp_name == "Students":
                            return redirect("accounts:student_dashboard")
                        elif grp_name == "Teachers":
                            return redirect("accounts:teacher_all_sessions")
                        elif grp_name == "Coordinators":
                            return redirect("accounts:coordinator_dashboard")
                        elif grp_name == "Super Coordinators":
                            return redirect("accounts:supercoordinator_dashboard")
                    else:
                        return render(
                            request,
                            "registration/login.html",
                            {
                                "form": form,
                                "my_messages": {"error": "Invalid Credentials."},
                            },
                        )
            else:
                return render(
                    request,
                    "registration/login.html",
                    {
                        "form": form,
                        "my_messages": {"error": "Invalid Credentials."},
                    },
                )
        else:
            return render(
                request,
                "registration/login.html",
                {"form": form, "my_messages": {"error": "Invalid Credentials."}},
            )


@login_required(login_url="accounts:loginlink")
def logoutU(request):
    logout(request)
    return redirect("accounts:loginlink")


@registration_data_cleanup
@redirect_to_dashboard
def registration(request):
    if request.method == "GET":
        form = RegistrationForm()
        return render(request, "registration/registration.html", {"form": form})
    else:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            dob = request.POST["dob"]
            request.session["dob"] = dob
            request.session["registration_visited"] = True
            if is_adult_func(dob) == "True":
                return redirect("accounts:consent_adult")
            else:
                return redirect("accounts:consent")
        else:
            return render(request, "registration/registration.html", {"form": form})


@redirect_to_dashboard
def consent(request):
    if "registration_visited" not in request.session:
        return redirect("accounts:registration")
    if request.method == "GET":
        if request.session.get("consent_data"):
            form = ConsentForm(request.session.get("consent_data"))
        else:
            form = ConsentForm()
        return render(
            request, "registration/consent.html", {"form": form, "is_adult": False}
        )
    else:
        form = ConsentForm(request.POST)
        if form.is_valid():
            request.session["consent_visited"] = True
            request.session["consent_data"] = request.POST
            return redirect("accounts:students_info")
        else:
            return render(
                request, "registration/consent.html", {"form": form, "is_adult": False}
            )


@redirect_to_dashboard
def consent_adult(request):
    if "registration_visited" not in request.session:
        return redirect("accounts:registration")
    if request.method == "GET":
        if request.session.get("consent_data"):
            form = ConsentForm(request.session.get("consent_data"))
        else:
            form = ConsentForm()
        return render(
            request, "registration/consent.html", {"form": form, "is_adult": True}
        )
    else:
        form = ConsentForm(request.POST)
        if form.is_valid():
            request.session["consent_visited"] = True
            request.session["consent_data"] = request.POST
            return redirect("accounts:students_info_adult")
        else:
            return render(
                request, "registration/consent.html", {"form": form, "is_adult": True}
            )


@redirect_to_dashboard
def parents_info(request):
    if "registration_visited" not in request.session:
        return redirect("accounts:registration")
    if "consent_visited" not in request.session:
        return redirect("accounts:consent")
    if request.method == "GET":
        if request.session.get("data"):
            form = ParentsInfoForm(request.session.get("data"))
            user_creation_form = UserCreationForm(request.session.get("data"))
        else:
            form = ParentsInfoForm()
            user_creation_form = UserCreationForm()
        return render(
            request,
            "registration/parents_info.html",
            {
                "form": form,
                "user_creation_form": user_creation_form,
            },
        )
    else:
        form = ParentsInfoForm(request.POST)
        user_creation_form = UserCreationForm(request.POST)

        if form.is_valid() and user_creation_form.is_valid():
            request.session["data"] = request.POST
            request.session["parents_info_visited"] = True
            return redirect("accounts:students_info")
        else:
            return render(
                request,
                "registration/parents_info.html",
                {
                    "form": form,
                    "user_creation_form": user_creation_form,
                },
            )


@redirect_to_dashboard
def students_info(request, is_adult=False):
    if is_adult:
        if "registration_visited" not in request.session:
            return redirect("accounts:registration")
        if "consent_visited" not in request.session:
            return redirect("accounts:consent_adult")
    else:
        if "registration_visited" not in request.session:
            return redirect("accounts:registration")
        if "consent_visited" not in request.session:
            return redirect("accounts:consent")
        if "parents_info_visited" not in request.session:
            return redirect("accounts:parents_info")
    student_dob = request.session["dob"]
    if request.method == "GET":
        form = StudentsInfoForm()
        form.fields["dob"].initial = student_dob
        form.fields["dob"].disabled = True
        user_creation_form = UserCreationForm()
        return render(
            request,
            "registration/students_info.html",
            {
                "form": form,
                "user_creation_form": user_creation_form,
                "is_adult": is_adult,
                "valid_state": True,
                "valid_city": True,
                "state": "",
                "city": "",
            },
        )
    else:
        if not is_adult:
            previousPOST = request.session["data"]
            form = StudentsInfoForm(request.POST)
            form.fields["dob"].initial = student_dob
            form.fields["dob"].disabled = True
            studentuserform = UserCreationForm(request.POST)
            parentform = ParentsInfoForm(previousPOST)
            parentuserform = UserCreationForm(previousPOST)
            if form.is_valid() and studentuserform.is_valid():
                temp = check_state_city(True, 0, str(request.POST["state"]))
                if temp[0]:
                    if not check_state_city(False, temp[1], str(request.POST["city"])):
                        return render(
                            request,
                            "registration/students_info.html",
                            {
                                "form": form,
                                "user_creation_form": studentuserform,
                                "is_adult": is_adult,
                                "valid_state": True,
                                "valid_city": False,
                                "state": request.POST["state"],
                                "city": request.POST["city"],
                            },
                        )
                else:
                    return render(
                        request,
                        "registration/students_info.html",
                        {
                            "form": form,
                            "user_creation_form": studentuserform,
                            "is_adult": is_adult,
                            "valid_state": False,
                            "valid_city": True,
                            "state": request.POST["state"],
                            "city": request.POST["city"],
                        },
                    )
                parentUser = parentuserform.save(commit=False)
                parentUser.save()
                parent_group = Group.objects.get(name="Parents")
                parentUser.groups.add(parent_group)
                parentUser.save()

                parent = parentform.save(commit=False)
                parent.user = parentUser
                parent.email = encryptionHelper.encrypt(previousPOST["email"])
                parent.fname = encryptionHelper.encrypt(previousPOST["fname"])
                parent.mname = encryptionHelper.encrypt(previousPOST["mname"])
                parent.lname = encryptionHelper.encrypt(previousPOST["lname"])
                parent.aadhar = encryptionHelper.encrypt(previousPOST["aadhar"])
                parent.dob = encryptionHelper.encrypt(previousPOST["dob"])
                parent.mobile_no = encryptionHelper.encrypt(previousPOST["mobile_no"])
                parent.gender = encryptionHelper.encrypt(previousPOST["gender"])
                parent.profile_pic = "accounts/default.svg"
                parent.consent = True
                parent.save()

                studentuser = studentuserform.save(commit=False)
                studentuser.save()
                student_group = Group.objects.get(name="Students")
                studentuser.groups.add(student_group)
                studentuser.save()

                student = form.save(commit=False)
                student.user = studentuser
                student.unique_no = encryptionHelper.encrypt(request.POST["unique_no"])
                student.fname = encryptionHelper.encrypt(request.POST["fname"])
                student.mname = encryptionHelper.encrypt(request.POST["mname"])
                student.lname = encryptionHelper.encrypt(request.POST["lname"])
                student.email = encryptionHelper.encrypt(request.POST["email"])
                student.dob = encryptionHelper.encrypt(student_dob)
                student.aadhar = encryptionHelper.encrypt(request.POST["aadhar"])
                student.mobile_no = encryptionHelper.encrypt(request.POST["mobile_no"])
                student.gender = encryptionHelper.encrypt(request.POST["gender"])
                student.adult = encryptionHelper.encrypt(is_adult_func(student_dob))
                student.state = State.objects.get(state=request.POST["state"])
                student.city = City.objects.get(city=request.POST["city"])
                student.pincode = encryptionHelper.encrypt(request.POST["pincode"])
                student.profile_pic = "accounts/default.svg"
                student.consent = True
                student.parent = parent
                student.save()

                user = authenticate(
                    request,
                    username=previousPOST["username"],
                    password=previousPOST["password1"],
                )
                request.session.set_expiry(86400)
                if user is not None:
                    login(request, user)

                del request.session["consent_data"]
                del request.session["data"]
                del request.session["dob"]
                del request.session["registration_visited"]
                del request.session["consent_visited"]
                del request.session["parents_info_visited"]
                return redirect("accounts:parent_dashboard")
            else:
                return render(
                    request,
                    "registration/students_info.html",
                    {
                        "form": form,
                        "user_creation_form": studentuserform,
                        "is_adult": is_adult,
                        "valid_state": True,
                        "valid_city": True,
                        "state": request.POST["state"],
                        "city": request.POST["city"],
                    },
                )
        else:
            form = StudentsInfoForm(request.POST)
            form.fields["dob"].initial = student_dob
            form.fields["dob"].disabled = True
            studentuserform = UserCreationForm(request.POST)
            if form.is_valid() and studentuserform.is_valid():
                temp = check_state_city(True, 0, str(request.POST["state"]))
                if temp[0]:
                    if not check_state_city(False, temp[1], str(request.POST["city"])):
                        return render(
                            request,
                            "registration/students_info.html",
                            {
                                "form": form,
                                "user_creation_form": studentuserform,
                                "is_adult": is_adult,
                                "valid_state": True,
                                "valid_city": False,
                                "state": request.POST["state"],
                                "city": request.POST["city"],
                            },
                        )
                else:
                    return render(
                        request,
                        "registration/students_info.html",
                        {
                            "form": form,
                            "user_creation_form": studentuserform,
                            "is_adult": is_adult,
                            "valid_state": False,
                            "valid_city": True,
                            "state": request.POST["state"],
                            "city": request.POST["city"],
                        },
                    )
                studentuser = studentuserform.save(commit=False)
                studentuser.save()
                student_group = Group.objects.get(name="Students")
                studentuser.groups.add(student_group)
                studentuser.save()

                student = form.save(commit=False)
                student.user = studentuser
                student.unique_no = encryptionHelper.encrypt(request.POST["unique_no"])
                student.fname = encryptionHelper.encrypt(request.POST["fname"])
                student.mname = encryptionHelper.encrypt(request.POST["mname"])
                student.lname = encryptionHelper.encrypt(request.POST["lname"])
                student.email = encryptionHelper.encrypt(request.POST["email"])
                student.aadhar = encryptionHelper.encrypt(request.POST["aadhar"])
                student.dob = encryptionHelper.encrypt(student_dob)
                student.mobile_no = encryptionHelper.encrypt(request.POST["mobile_no"])
                student.gender = encryptionHelper.encrypt(request.POST["gender"])
                student.adult = encryptionHelper.encrypt(is_adult_func(student_dob))
                student.state = State.objects.get(state=request.POST["state"])
                student.city = City.objects.get(city=request.POST["city"])
                student.pincode = encryptionHelper.encrypt(request.POST["pincode"])
                student.profile_pic = "accounts/default.svg"
                student.consent = True
                student.save()

                user = authenticate(
                    request,
                    username=request.POST["username"],
                    password=request.POST["password1"],
                )
                request.session.set_expiry(86400)
                if user is not None:
                    login(request, user)

                del request.session["consent_data"]
                del request.session["dob"]
                del request.session["registration_visited"]
                del request.session["consent_visited"]
                return redirect("accounts:student_dashboard")
            else:
                return render(
                    request,
                    "registration/students_info.html",
                    {
                        "form": form,
                        "user_creation_form": studentuserform,
                        "is_adult": is_adult,
                        "valid_state": True,
                        "valid_city": True,
                        "state": request.POST["state"],
                        "city": request.POST["city"],
                    },
                )


@redirect_to_dashboard
def students_info_adult(request):
    return students_info(request, True)


@login_required(login_url="accounts:loginlink")
@user_passes_test(is_admin, login_url="accounts:forbidden")
def addSuperCoordinatorForm(request):
    if request.method == "GET":
        form = SuperCoordinatorsInfoForm()
        user_creation_form = UserCreationForm()
        return render(
            request,
            "registration/add_supercoordinator.html",
            {"form": form, "user_creation_form": user_creation_form},
        )
    else:
        form = SuperCoordinatorsInfoForm(request.POST)
        supercoordinatoruserform = UserCreationForm(request.POST)
        if form.is_valid() and supercoordinatoruserform.is_valid():
            supercoordinatoruser = supercoordinatoruserform.save(commit=False)
            supercoordinatoruser.save()
            supercoordinator_group = Group.objects.get(name="Super Coordinators")
            supercoordinatoruser.groups.add(supercoordinator_group)
            supercoordinatoruser.save()
            supercoordinator = form.save(commit=False)
            supercoordinator.user = supercoordinatoruser
            supercoordinator.email = encryptionHelper.encrypt(request.POST["email"])
            supercoordinator.fname = encryptionHelper.encrypt(request.POST["fname"])
            supercoordinator.mname = encryptionHelper.encrypt(request.POST["mname"])
            supercoordinator.lname = encryptionHelper.encrypt(request.POST["lname"])
            supercoordinator.aadhar = encryptionHelper.encrypt(request.POST["aadhar"])
            supercoordinator.dob = encryptionHelper.encrypt(request.POST["dob"])
            supercoordinator.gender = encryptionHelper.encrypt(request.POST["gender"])
            supercoordinator.mobile_no = encryptionHelper.encrypt(
                request.POST["mobile_no"]
            )
            supercoordinator.profile_pic = "accounts/default.svg"
            supercoordinator.save()
            return redirect("accounts:add_supercoordinator_form")
        else:
            return render(
                request,
                "registration/add_supercoordinator.html",
                {"form": form, "user_creation_form": supercoordinatoruserform},
            )


@login_required(login_url="accounts:loginlink")
@user_passes_test(
    lambda user: is_parent(user) or (is_student(user) and is_adult_student(user)),
    login_url="accounts:forbidden",
)
def give_consent(request):
    if request.method == "GET":
        if is_student(request.user):
            student = StudentsInfo.objects.filter(user=request.user).first()
            initial_dic = {"consent": student.consent}
        else:
            parent = ParentsInfo.objects.filter(user=request.user).first()
            initial_dic = {"consent": parent.consent}
        form = ConsentForm(initial=initial_dic)
        return render(request, "registration/give_consent.html", {"form": form})
    else:
        form = ConsentForm(request.POST)
        if form.is_valid():
            if is_student(request.user):
                student = StudentsInfo.objects.filter(user=request.user).first()
                student.consent = True
                student.save()
            else:
                parent = ParentsInfo.objects.filter(user=request.user).first()
                parent.consent = True
                parent.save()
                students = StudentsInfo.objects.filter(parent=parent)
                for i in students:
                    i.consent = True
                    i.save()
            return redirect("accounts:loginlink")
        else:
            return render(request, "registration/give_consent.html", {"form": form})


@login_required(login_url="accounts:loginlink")
@user_passes_test(
    lambda user: is_student(user) and not is_adult_student(user),
    login_url="accounts:forbidden",
)
def ask_to_give_consent(request):
    return render(request, "registration/ask_to_give_consent.html", {})
