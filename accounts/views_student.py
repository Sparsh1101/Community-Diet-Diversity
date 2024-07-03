from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .decorators import *
from .helper_functions import *
from .models import *
from .forms import *
from shared.encryption import EncryptionHelper
from django.conf import settings

encryptionHelper = EncryptionHelper()


@login_required(login_url="accounts:loginlink")
@user_passes_test(is_student, login_url="accounts:forbidden")
@consent
@password_change_required
@secondary_reg
def student_dashboard(request):
    return render(
        request,
        "student/student_dashboard.html",
        {"page_type": "student_dashboard"},
    )


@login_required(login_url="accounts:loginlink")
@user_passes_test(
    lambda user: is_student(user),
    login_url="accounts:forbidden",
)
@consent
@password_change_required
@secondary_reg
def view_student_profile(request):
    if request.method == "GET":
        user = request.user
        if is_student(user):
            student = StudentsInfo.objects.filter(user=user).first()

            student.fname = encryptionHelper.decrypt(student.fname)
            student.lname = encryptionHelper.decrypt(student.lname)
            student.unique_no = encryptionHelper.decrypt(student.unique_no)

            if student.mname:
                student.mname = encryptionHelper.decrypt(student.mname)
                if student.mname == "":
                    student.mname = ""
            else:
                student.mname = ""

            if student.aadhar:
                student.aadhar = encryptionHelper.decrypt(student.aadhar)
                if student.aadhar == "":
                    student.aadhar = "-"
            else:
                student.aadhar = "-"

            if student.email:
                student.email = encryptionHelper.decrypt(student.email)
                if student.email == "":
                    student.email = "-"
            else:
                student.email = "-"

            if student.mobile_no:
                student.mobile_no = encryptionHelper.decrypt(student.mobile_no)
                if student.mobile_no == "":
                    student.mobile_no = "-"
            else:
                student.mobile_no = "-"

            student.dob = encryptionHelper.decrypt(student.dob)
            student.gender = encryptionHelper.decrypt(student.gender)
            student.pincode = encryptionHelper.decrypt(student.pincode)

            return render(
                request,
                "student/view_student_profile.html",
                {"page_type": "view_student_profile", "student": student},
            )


@login_required(login_url="accounts:loginlink")
@user_passes_test(
    lambda user: is_student(user),
    login_url="accounts:forbidden",
)
@consent
@password_change_required
@secondary_reg
def edit_student_profile(request):
    student = StudentsInfo.objects.filter(user=request.user).first()
    adult = encryptionHelper.decrypt(student.adult)
    adult = True if adult == "True" else False
    if request.method == "GET":
        initial_dict = {
            "fname": encryptionHelper.decrypt(student.fname),
            "lname": encryptionHelper.decrypt(student.lname),
            "profile_pic": student.profile_pic,
            "dob": encryptionHelper.decrypt(student.dob),
            "gender": encryptionHelper.decrypt(student.gender),
            "pincode": encryptionHelper.decrypt(student.pincode),
            "unique_no": encryptionHelper.decrypt(student.unique_no),
            "organization": student.organization,
        }

        initial_dict_2 = {
            "occupation": student.secondary_reg.occupation
            if student.secondary_reg.occupation
            else "",
            "edu": student.secondary_reg.edu if student.secondary_reg.edu else "",
            "no_of_family_members": student.secondary_reg.no_of_family_members
            if student.secondary_reg.no_of_family_members
            else "",
            "type_of_family": student.secondary_reg.type_of_family
            if student.secondary_reg.type_of_family
            else "",
            "religion": student.secondary_reg.religion
            if student.secondary_reg.religion
            else "",
            "family_income": student.secondary_reg.family_income
            if student.secondary_reg.family_income
            else "",
            "ration_card_color": student.secondary_reg.ration_card_color
            if student.secondary_reg.ration_card_color
            else "",
        }

        if student.mname:
            initial_dict["mname"] = encryptionHelper.decrypt(student.mname)
        if student.aadhar:
            initial_dict["aadhar"] = encryptionHelper.decrypt(student.aadhar)
        if student.email:
            initial_dict["email"] = encryptionHelper.decrypt(student.email)
        if student.mobile_no:
            initial_dict["mobile_no"] = encryptionHelper.decrypt(student.mobile_no)

        form = StudentsInfoForm(request.POST or None, initial=initial_dict)
        form2 = SecondaryRegForm(initial=initial_dict_2)
        form.fields["organization"].disabled = True
        form.fields["dob"].disabled = True

        return render(
            request,
            "student/update_students_info.html",
            {
                "form": form,
                "form2": form2,
                "adult": adult,
                "valid_state": True,
                "valid_city": True,
                "state": student.state,
                "city": student.city,
            },
        )
    else:
        form = StudentsInfoForm(request.POST, request.FILES)
        form.fields["organization"].disabled = True
        form.fields["organization"].initial = student.organization
        form.fields["dob"].disabled = True
        form.fields["dob"].initial = encryptionHelper.decrypt(student.dob)

        form2 = SecondaryRegForm(request.POST)
        if form.is_valid() and form2.is_valid():
            temp = check_state_city(True, 0, str(request.POST["state"]))
            if temp[0]:
                if not check_state_city(False, temp[1], str(request.POST["city"])):
                    return render(
                        request,
                        "student/update_students_info.html",
                        {
                            "form": form,
                            "form2": form2,
                            "adult": adult,
                            "valid_state": True,
                            "valid_city": False,
                            "state": request.POST["state"],
                            "city": request.POST["city"],
                        },
                    )
            else:
                return render(
                    request,
                    "student/update_students_info.html",
                    {
                        "form": form,
                        "form2": form2,
                        "adult": adult,
                        "valid_state": False,
                        "valid_city": True,
                        "state": request.POST["state"],
                        "city": request.POST["city"],
                    },
                )

            student = StudentsInfo.objects.filter(user=request.user).first()

            if student.mname:
                student.mname = encryptionHelper.encrypt(request.POST["mname"])
            if student.aadhar:
                student.aadhar = encryptionHelper.encrypt(request.POST["aadhar"])
            if student.email:
                student.email = encryptionHelper.encrypt(request.POST["email"])
            if student.mobile_no:
                student.mobile_no = encryptionHelper.encrypt(request.POST["mobile_no"])

            student.fname = encryptionHelper.encrypt(request.POST["fname"])
            student.lname = encryptionHelper.encrypt(request.POST["lname"])
            student.unique_no = encryptionHelper.encrypt(request.POST["unique_no"])
            student.gender = encryptionHelper.encrypt(request.POST["gender"])

            student.state = State.objects.get(
                state__icontains=request.POST["state"].strip()
            )
            student.city = City.objects.get(
                city__icontains=request.POST["city"].strip()
            )
            student.pincode = encryptionHelper.encrypt(request.POST["pincode"])

            if request.FILES:
                if request.FILES["profile_pic"].size > 5 * 1024 * 1024:
                    form.add_error("profile_pic", "File size must be less than 5MB.")

                    return render(
                        request,
                        "student/update_students_info.html",
                        {
                            "form": form,
                            "form2": form2,
                            "adult": adult,
                            "valid_state": True,
                            "valid_city": True,
                            "state": request.POST["state"],
                            "city": request.POST["city"],
                        },
                    )
                else:
                    x = student.profile_pic.url.split("/media/accounts/")
                    if x[1] != "default.svg":
                        file = settings.MEDIA_ROOT + "/accounts/" + x[1]
                        os.remove(file)
                    student.profile_pic = request.FILES["profile_pic"]
            else:
                if "profile_pic-clear" in request.POST.keys():
                    x = student.profile_pic.url.split("/media/accounts/")
                    if x[1] != "default.svg":
                        file = settings.MEDIA_ROOT + "/accounts/" + x[1]
                        os.remove(file)
                    student.profile_pic = "accounts/default.svg"

            secondary_reg = form2.save(commit=False)
            secondary_reg.no_of_family_members = request.POST["no_of_family_members"]
            secondary_reg.save()
            student.secondary_reg = secondary_reg
            student.save()
            return redirect("accounts:view_student_profile")

        else:
            return render(
                request,
                "student/update_students_info.html",
                {
                    "form": form,
                    "form2": form2,
                    "adult": adult,
                    "valid_state": True,
                    "valid_city": True,
                    "state": request.POST["state"],
                    "city": request.POST["city"],
                },
            )


@login_required(login_url="accounts:loginlink")
@user_passes_test(
    lambda user: is_student(user),
    login_url="accounts:forbidden",
)
@consent
@password_change_required
def secondary_registration(request):
    student = StudentsInfo.objects.filter(user=request.user).first()
    adult = encryptionHelper.decrypt(student.adult)
    adult = True if adult == "True" else False
    if request.method == "GET":
        if student.secondary_reg == None:
            form = SecondaryRegForm()
        else:
            initial_dict = {
                "occupation": student.secondary_reg.occupation
                if student.secondary_reg.occupation
                else "",
                "edu": student.secondary_reg.edu if student.secondary_reg.edu else "",
                "no_of_family_members": student.secondary_reg.no_of_family_members
                if student.secondary_reg.no_of_family_members
                else "",
                "type_of_family": student.secondary_reg.type_of_family
                if student.secondary_reg.type_of_family
                else "",
                "religion": student.secondary_reg.religion
                if student.secondary_reg.religion
                else "",
                "family_income": student.secondary_reg.family_income
                if student.secondary_reg.family_income
                else "",
                "ration_card_color": student.secondary_reg.ration_card_color
                if student.secondary_reg.ration_card_color
                else "",
            }
            form = SecondaryRegForm(initial=initial_dict)
        return render(
            request,
            "student/secondary_registration.html",
            {"form": form, "adult": adult},
        )
    else:
        form = SecondaryRegForm(request.POST)
        if form.is_valid():
            secondary_reg = form.save(commit=False)
            secondary_reg.no_of_family_members = request.POST["no_of_family_members"]
            secondary_reg.save()
            student.secondary_reg = secondary_reg
            student.save()
            return redirect("accounts:view_student_profile")
        else:
            return render(
                request,
                "student/secondary_registration.html",
                {"form": form, "adult": adult},
            )
