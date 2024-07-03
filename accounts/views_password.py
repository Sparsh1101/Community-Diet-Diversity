from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.password_validation import validate_password
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.core.exceptions import ValidationError
from .decorators import *
from .models import *
from .forms import *
from .helper_functions import *
from .token import password_reset_token
from shared.encryption import EncryptionHelper
import random
from django.conf import settings

encryptionHelper = EncryptionHelper()


def reset_password_emailer(request, user, user_email):
    site = get_current_site(request)
    token = password_reset_token.make_token(user)
    link = request.META.get("HTTP_REFERER")
    if link[:4] == "http":
        if link[:5] == "https":
            protocol = "https://"
        else:
            protocol = "http://"
    else:
        protocol = ""
    message = get_template("password/email_template.html",).render(
        {
            "user": user,
            "protocol": protocol,
            "domain": site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": token,
        }
    )
    msg = EmailMessage(
        "Community Diet Diversity Reset Password, Ref Token: " + str(token),
        message,
        settings.FROM_EMAIL_ID,
        [str(user_email)],
    )
    msg.content_subtype = "html"
    msg.send(fail_silently=True)


@registration_data_cleanup
@redirect_to_dashboard
def forgot_password(request):
    if request.method == "GET":
        form = forgot_password_form()
        return render(request, "password/forgot_password.html", {"form": form})
    else:
        form = forgot_password_form(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                our_user = custom_user_filter(user)
                if our_user == None:
                    form.add_error(
                        "username", "Sorry but the following user cannot be serviced."
                    )
                    return render(
                        request, "password/forgot_password.html", {"form": form}
                    )
                else:
                    user_email = encryptionHelper.decrypt(our_user[0].email)
                    if user_email == "":
                        request.session["forgot_password"] = {
                            "username": username,
                            "attempts_count": 0,
                            "display_form": True,
                        }
                        return redirect("accounts:forgot_password_questions")
                    else:
                        reset_password_emailer(request, user, user_email)
                        return render(
                            request,
                            "password/forgot_password.html",
                            {
                                "form": form,
                                "my_messages": {
                                    "success": "Mail has been sent on the email ID provided during registration. Please click on the link sent via mail to change password. The link will expire in 10 minutes."
                                },
                                "user_type": our_user[1],
                            },
                        )
            else:
                form.add_error("username", "Invalid Username.")
                return render(request, "password/forgot_password.html", {"form": form})
        else:
            return render(request, "password/forgot_password.html", {"form": form})


def forgot_password_final(request, uidb64, token):
    if request.method == "GET":
        form = forgot_password_email_form()
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except:
            return render(
                request,
                "password/forgot_password_final.html",
                {"form": form, "my_messages": {"error": "Invalid URL."}},
            )
        if not password_reset_token.check_token(user, token):
            return render(
                request,
                "password/forgot_password_final.html",
                {
                    "form": form,
                    "my_messages": {
                        "error": "Either the link used is invalid or reset password timedout. Please request a new password reset."
                    },
                },
            )
        return render(request, "password/forgot_password_final.html", {"form": form})
    else:
        form = forgot_password_email_form(request.POST)
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except:
            return render(
                request,
                "password/forgot_password_final.html",
                {"form": form, "my_messages": {"error": "Invalid URL."}},
            )
        if password_reset_token.check_token(user, token):
            if form.is_valid():
                password1 = form.cleaned_data["password1"]
                password2 = form.cleaned_data["password2"]
                if not user.check_password(password1):
                    try:
                        validate_password(password1)
                        if password1 == password2:
                            user.set_password(password1)
                            user.save()
                            return redirect("accounts:password_changed")
                        else:
                            form.add_error("password2", "Both passwords didn't match!")
                            return render(
                                request,
                                "password/forgot_password_final.html",
                                {"form": form},
                            )
                    except ValidationError as e:
                        form.add_error("password1", e)
                        return render(
                            request,
                            "password/forgot_password_final.html",
                            {"form": form},
                        )
                else:
                    form.add_error(
                        "password1", "Password entered is same as the previous one!"
                    )
                    return render(
                        request, "password/forgot_password_final.html", {"form": form}
                    )
            else:
                return render(
                    request, "password/forgot_password_final.html", {"form": form}
                )
        else:
            return render(
                request,
                "password/forgot_password_final.html",
                {
                    "form": form,
                    "my_messages": {
                        "error": "Either the link used is invalid or expired. Please re-request password reset."
                    },
                },
            )


def forgot_password_questions(request):
    if not "forgot_password" in request.session:
        return redirect("accounts:forbidden")
    user = User.objects.get(username=request.session["forgot_password"]["username"])
    our_user = custom_user_filter(user)
    if request.method == "GET":
        my_messages = False
        if request.session["forgot_password"]["attempts_count"] == 2:
            return render(
                request,
                "password/forgot_password_questions.html",
                {
                    "attempts_exhausted": True,
                    "user_type": our_user[1],
                    "my_messages": my_messages,
                },
            )
        elif request.session["forgot_password"]["display_form"] == False:
            return render(
                request,
                "password/forgot_password_questions.html",
                {"user_type": our_user[1], "my_messages": my_messages},
            )
        elif request.session["forgot_password"]["attempts_count"] == 1:
            my_messages = True
        if (
            our_user[1] == "Super Coordinators"
            or our_user[1] == "Coordinators"
            or our_user[1] == "Teachers"
        ):
            if our_user[0].aadhar and our_user[0].mobile_no:
                our_user[0].aadhar = encryptionHelper.decrypt(our_user[0].aadhar)
                if our_user[0].aadhar == "":
                    request.session["forgot_password"]["display_form"] = False
                    request.session.modified = True
                    return render(
                        request,
                        "password/forgot_password_questions.html",
                        {"user_type": our_user[1], "my_messages": my_messages},
                    )
                our_user[0].mobile_no = encryptionHelper.decrypt(our_user[0].mobile_no)
                if our_user[0].mobile_no == "":
                    request.session["forgot_password"]["display_form"] = False
                    request.session.modified = True
                    return render(
                        request,
                        "password/forgot_password_questions.html",
                        {"user_type": our_user[1], "my_messages": my_messages},
                    )
                return render(
                    request,
                    "password/forgot_password_questions.html",
                    {
                        "display_form": True,
                        "user_type": our_user[1],
                        "aadhar": True,
                        "mobile_no": True,
                        "dob": True,
                        "my_messages": my_messages,
                    },
                )
            else:
                request.session["forgot_password"]["display_form"] = False
                request.session.modified = True
                return render(
                    request,
                    "password/forgot_password_questions.html",
                    {"user_type": our_user[1], "my_messages": my_messages},
                )
        elif our_user[1] == "Parents":
            context = {
                "display_form": True,
                "user_type": our_user[1],
                "my_messages": my_messages,
            }
            available_fields = [
                "dob",
                "student_username",
                "student_dob",
                "student_unique_no",
                "student_pincode",
            ]
            if our_user[0].aadhar:
                our_user[0].aadhar = encryptionHelper.decrypt(our_user[0].aadhar)
                if our_user[0].aadhar != "":
                    available_fields.append("aadhar")
            if our_user[0].mobile_no:
                our_user[0].mobile_no = encryptionHelper.decrypt(our_user[0].mobile_no)
                if our_user[0].mobile_no != "":
                    available_fields.append("mobile_no")
            children = StudentsInfo.objects.filter(parent=our_user[0])
            for child in children:
                if child.secondary_reg != None:
                    if (
                        child.secondary_reg.occupation != None
                        and "occupation" not in available_fields
                    ):
                        available_fields.append("occupation")
                    if (
                        child.secondary_reg.edu != None
                        and "edu" not in available_fields
                    ):
                        available_fields.append("edu")
                    if (
                        child.secondary_reg.no_of_family_members != None
                        and "no_of_family_members" not in available_fields
                    ):
                        available_fields.append("no_of_family_members")
                    if (
                        child.secondary_reg.type_of_family != None
                        and "type_of_family" not in available_fields
                    ):
                        available_fields.append("type_of_family")
                    if (
                        child.secondary_reg.religion != None
                        and "religion" not in available_fields
                    ):
                        available_fields.append("religion")
                    if (
                        child.secondary_reg.family_income != None
                        and "family_income" not in available_fields
                    ):
                        available_fields.append("family_income")
                    if (
                        child.secondary_reg.ration_card_color != None
                        and "ration_card_color" not in available_fields
                    ):
                        available_fields.append("ration_card_color")
                if child.aadhar:
                    child.aadhar = encryptionHelper.decrypt(child.aadhar)
                    if child.aadhar != "" and "student_aadhar" not in available_fields:
                        available_fields.append("student_aadhar")
                if child.mobile_no:
                    child.mobile_no = encryptionHelper.decrypt(child.mobile_no)
                    if (
                        child.mobile_no != ""
                        and "student_mobile_no" not in available_fields
                    ):
                        available_fields.append("student_mobile_no")
                if child.email:
                    child.email = encryptionHelper.decrypt(child.email)
                    if child.email != "" and "student_email" not in available_fields:
                        available_fields.append("student_email")
            selected_fields = []
            for i in range(3):
                choice = random.choice(available_fields)
                available_fields.remove(choice)
                selected_fields.append(choice)
            request.session["forgot_password"]["fields"] = selected_fields
            request.session.modified = True
            for i in selected_fields:
                if i in [
                    "occupation",
                    "edu",
                    "religion",
                    "type_of_family",
                    "family_income",
                    "ration_card_color",
                ]:
                    context[i] = True
                    if i == "occupation":
                        context["occupation_list"] = list(
                            Occupation.objects.values_list("occupation", flat=True)
                        )
                    elif i == "edu":
                        context["edu_list"] = list(
                            Education.objects.values_list("education", flat=True)
                        )
                    elif i == "religion":
                        context["religion_list"] = list(
                            ReligiousBelief.objects.values_list("religion", flat=True)
                        )
                    elif i == "type_of_family":
                        context["type_of_family_list"] = list(
                            FamilyType.objects.values_list("family", flat=True)
                        )
                    elif i == "family_income":
                        context["family_income_list"] = list(
                            FamilyIncome.objects.values_list("family_income", flat=True)
                        )
                    elif i == "ration_card_color":
                        context["ration_card_color_list"] = list(
                            RationCardColor.objects.values_list(
                                "ration_card_color", flat=True
                            )
                        )
                else:
                    context[i] = True
            return render(request, "password/forgot_password_questions.html", context)
        else:
            context = {
                "display_form": True,
                "user_type": our_user[1],
                "my_messages": my_messages,
            }
            available_fields = [
                "dob",
                "unique_no",
                "pincode",
                "parent_username",
                "parent_dob",
            ]
            if our_user[0].aadhar:
                our_user[0].aadhar = encryptionHelper.decrypt(our_user[0].aadhar)
                if our_user[0].aadhar != "":
                    available_fields.append("aadhar")
            if our_user[0].mobile_no:
                our_user[0].mobile_no = encryptionHelper.decrypt(our_user[0].mobile_no)
                if our_user[0].mobile_no != "":
                    available_fields.append("mobile_no")
            if our_user[0].secondary_reg != None:
                if our_user[0].secondary_reg.occupation != None:
                    available_fields.append("occupation")
                if our_user[0].secondary_reg.edu != None:
                    available_fields.append("edu")
                if our_user[0].secondary_reg.no_of_family_members != None:
                    available_fields.append("no_of_family_members")
                if our_user[0].secondary_reg.type_of_family != None:
                    available_fields.append("type_of_family")
                if our_user[0].secondary_reg.religion != None:
                    available_fields.append("religion")
                if our_user[0].secondary_reg.family_income != None:
                    available_fields.append("family_income")
                if our_user[0].secondary_reg.ration_card_color != None:
                    available_fields.append("ration_card_color")
            if our_user[0].parent != None:
                if our_user[0].parent.aadhar:
                    our_user[0].parent.aadhar = encryptionHelper.decrypt(
                        our_user[0].parent.aadhar
                    )
                    if our_user[0].parent.aadhar != "":
                        available_fields.append("parent_aadhar")
                if our_user[0].parent.email:
                    our_user[0].parent.email = encryptionHelper.decrypt(
                        our_user[0].parent.email
                    )
                    if our_user[0].parent.email != "":
                        available_fields.append("parent_email")
                if our_user[0].parent.mobile_no:
                    our_user[0].parent.mobile_no = encryptionHelper.decrypt(
                        our_user[0].parent.mobile_no
                    )
                    if our_user[0].parent.mobile_no != "":
                        available_fields.append("parent_mobile_no")
            selected_fields = []
            for i in range(3):
                choice = random.choice(available_fields)
                available_fields.remove(choice)
                selected_fields.append(choice)
            request.session["forgot_password"]["fields"] = selected_fields
            request.session.modified = True
            for i in selected_fields:
                if i in [
                    "occupation",
                    "edu",
                    "religion",
                    "type_of_family",
                    "family_income",
                    "ration_card_color",
                ]:
                    context[i] = True
                    if i == "occupation":
                        context["occupation_list"] = list(
                            Occupation.objects.values_list("occupation", flat=True)
                        )
                    elif i == "edu":
                        context["edu_list"] = list(
                            Education.objects.values_list("education", flat=True)
                        )
                    elif i == "religion":
                        context["religion_list"] = list(
                            ReligiousBelief.objects.values_list("religion", flat=True)
                        )
                    elif i == "type_of_family":
                        context["type_of_family_list"] = list(
                            FamilyType.objects.values_list("family", flat=True)
                        )
                    elif i == "family_income":
                        context["family_income_list"] = list(
                            FamilyIncome.objects.values_list("family_income", flat=True)
                        )
                    elif i == "ration_card_color":
                        context["ration_card_color_list"] = list(
                            RationCardColor.objects.values_list(
                                "ration_card_color", flat=True
                            )
                        )
                else:
                    context[i] = True
            return render(request, "password/forgot_password_questions.html", context)
    else:
        request.session["forgot_password"]["attempts_count"] += 1
        request.session.modified = True
        if (
            our_user[1] == "Super Coordinators"
            or our_user[1] == "Coordinators"
            or our_user[1] == "Teachers"
        ):
            if (
                request.POST["aadhar"] != encryptionHelper.decrypt(our_user[0].aadhar)
                or request.POST["mobile_no"]
                != encryptionHelper.decrypt(our_user[0].mobile_no)
                or request.POST["dob"] != encryptionHelper.decrypt(our_user[0].dob)
            ):
                return redirect("accounts:forgot_password_questions")
            else:
                del request.session["forgot_password"]
                return redirect(
                    "accounts:forgot_password_final",
                    urlsafe_base64_encode(force_bytes(user.pk)),
                    password_reset_token.make_token(user),
                )
        elif our_user[1] == "Parents":
            fields = request.session["forgot_password"]["fields"]
            valid = True
            children = StudentsInfo.objects.filter(parent=our_user[0])
            for i in fields:
                if (
                    (
                        i == "aadhar"
                        and request.POST["aadhar"]
                        != encryptionHelper.decrypt(our_user[0].aadhar)
                    )
                    or (
                        i == "mobile_no"
                        and request.POST["mobile_no"]
                        != encryptionHelper.decrypt(our_user[0].mobile_no)
                    )
                    or (
                        i == "dob"
                        and request.POST["dob"]
                        != encryptionHelper.decrypt(our_user[0].dob)
                    )
                ):
                    valid = False
                    break
                valid = False
                for child in children:
                    if (
                        (
                            i == "student_username"
                            and child.user.username == request.POST["student_username"]
                        )
                        or (
                            i == "student_aadhar"
                            and child.aadhar
                            and encryptionHelper.decrypt(child.aadhar)
                            == request.POST["student_aadhar"]
                        )
                        or (
                            i == "student_dob"
                            and encryptionHelper.decrypt(child.dob)
                            == request.POST["student_dob"]
                        )
                        or (
                            i == "student_unique_no"
                            and encryptionHelper.decrypt(child.unique_no)
                            == request.POST["student_unique_no"]
                        )
                        or (
                            i == "student_mobile_no"
                            and child.mobile_no
                            and encryptionHelper.decrypt(child.mobile_no)
                            == request.POST["student_mobile_no"]
                        )
                        or (
                            i == "student_pincode"
                            and encryptionHelper.decrypt(child.pincode)
                            == request.POST["student_pincode"]
                        )
                        or (
                            i == "student_email"
                            and child.email
                            and encryptionHelper.decrypt(child.email)
                            == request.POST["student_email"]
                        )
                        or (
                            (child.secondary_reg != None)
                            and (
                                (
                                    i == "occupation"
                                    and child.secondary_reg.occupation.occupation
                                    == request.POST["occupation"]
                                )
                                or (
                                    i == "edu"
                                    and child.secondary_reg.edu.education
                                    == request.POST["edu"]
                                )
                                or (
                                    i == "no_of_family_members"
                                    and child.secondary_reg.no_of_family_members
                                    == request.POST["no_of_family_members"]
                                )
                                or (
                                    i == "type_of_family"
                                    and child.secondary_reg.type_of_family.family
                                    == request.POST["type_of_family"]
                                )
                                or (
                                    i == "religion"
                                    and child.secondary_reg.religion.religion
                                    == request.POST["religion"]
                                )
                                or (
                                    i == "family_income"
                                    and child.secondary_reg.family_income.family_income
                                    == request.POST["family_income"]
                                )
                                or (
                                    i == "ration_card_color"
                                    and child.secondary_reg.ration_card_color.ration_card_color
                                    == request.POST["ration_card_color"]
                                )
                            )
                        )
                    ):
                        valid = True
                        break
            if valid:
                del request.session["forgot_password"]
                return redirect(
                    "accounts:forgot_password_final",
                    urlsafe_base64_encode(force_bytes(user.pk)),
                    password_reset_token.make_token(user),
                )
            else:
                return redirect("accounts:forgot_password_questions")
        else:
            fields = request.session["forgot_password"]["fields"]
            valid = True
            for i in fields:
                if (
                    (
                        i == "aadhar"
                        and request.POST["aadhar"]
                        != encryptionHelper.decrypt(our_user[0].aadhar)
                    )
                    or (
                        i == "mobile_no"
                        and request.POST["mobile_no"]
                        != encryptionHelper.decrypt(our_user[0].mobile_no)
                    )
                    or (
                        i == "dob"
                        and request.POST["dob"]
                        != encryptionHelper.decrypt(our_user[0].dob)
                    )
                    or (
                        i == "unique_no"
                        and request.POST["unique_no"]
                        != encryptionHelper.decrypt(our_user[0].unique_no)
                    )
                    or (
                        i == "pincode"
                        and request.POST["pincode"]
                        != encryptionHelper.decrypt(our_user[0].pincode)
                    )
                    or (
                        i == "occupation"
                        and request.POST["occupation"]
                        != our_user[0].secondary_reg.occupation.occupation
                    )
                    or (
                        i == "edu"
                        and request.POST["edu"]
                        != our_user[0].secondary_reg.edu.education
                    )
                    or (
                        i == "no_of_family_members"
                        and request.POST["no_of_family_members"]
                        != our_user[0].secondary_reg.no_of_family_members
                    )
                    or (
                        i == "type_of_family"
                        and request.POST["type_of_family"]
                        != our_user[0].secondary_reg.type_of_family.family
                    )
                    or (
                        i == "religion"
                        and request.POST["religion"]
                        != our_user[0].secondary_reg.religion.religion
                    )
                    or (
                        i == "family_income"
                        and request.POST["family_income"]
                        != our_user[0].secondary_reg.family_income.family_income
                    )
                    or (
                        i == "ration_card_color"
                        and request.POST["ration_card_color"]
                        != our_user[0].secondary_reg.ration_card_color.ration_card_color
                    )
                    or (
                        i == "parent_username"
                        and request.POST["parent_username"]
                        != our_user[0].parent.user.username
                    )
                    or (
                        i == "parent_dob"
                        and request.POST["parent_dob"]
                        != encryptionHelper.decrypt(our_user[0].parent.dob)
                    )
                    or (
                        i == "parent_aadhar"
                        and request.POST["parent_aadhar"]
                        != encryptionHelper.decrypt(our_user[0].parent.aadhar)
                    )
                    or (
                        i == "parent_email"
                        and request.POST["parent_email"]
                        != encryptionHelper.decrypt(our_user[0].parent.email)
                    )
                    or (
                        i == "parent_mobile_no"
                        and request.POST["parent_mobile_no"]
                        != encryptionHelper.decrypt(our_user[0].parent.mobile_no)
                    )
                ):
                    valid = False
                    break
            if valid:
                del request.session["forgot_password"]
                return redirect(
                    "accounts:forgot_password_final",
                    urlsafe_base64_encode(force_bytes(user.pk)),
                    password_reset_token.make_token(user),
                )
            else:
                return redirect("accounts:forgot_password_questions")


@login_required(login_url="accounts:loginlink")
@user_passes_test(
    lambda user: is_supercoordinator(user)
    or is_coordinator(user)
    or is_teacher(user)
    or is_parent(user)
    or is_student(user),
    login_url="accounts:forbidden",
)
@consent
def change_password(request):
    if request.method == "GET":
        form = change_password_form()
        return render(request, "password/change_password.html", {"form": form})
    else:
        form = change_password_form(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data["old_password"]
            new_password = form.cleaned_data["password"]
            user = request.user
            if user.check_password(old_password):
                try:
                    validate_password(new_password)
                    if user.check_password(new_password):
                        form.add_error(
                            "password", "Password entered is same as the previous one!"
                        )
                    else:
                        user.set_password(new_password)
                        user.save()
                        our_user = custom_user_filter(user)[0]
                        our_user.password_changed = True
                        our_user.first_password = ""
                        our_user.save()
                        logout(request)
                        return redirect("accounts:password_changed")
                except ValidationError as e:
                    form.add_error("password", e)
            else:
                form.add_error("old_password", "Incorrect Password")
        return render(request, "password/change_password.html", {"form": form})


def password_changed(request):
    return render(request, "password/password_changed.html", {})
