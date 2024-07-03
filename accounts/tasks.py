from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.utils import timezone
from shared.encryption import EncryptionHelper
from .models import *
from .helper_functions import *
from datetime import date
from django.conf import settings

encryptionHelper = EncryptionHelper()


@shared_task
def new_physique_form():
    physique_form_id = Form.objects.get(name="physique")
    if InfoFormDetails.objects.filter(open=True, form=physique_form_id).exists():
        oldform = InfoFormDetails.objects.get(open=True, form=physique_form_id)
        oldform.open = False
        oldform.end_timestamp = timezone.now()
        oldform.save()
    form = InfoFormDetails(start_timestamp=timezone.now())
    form.open = True
    form.form = physique_form_id
    form.save()
    students = StudentsInfo.objects.filter(session__isnull=False)
    required_students = []
    for student in students:
        if student.email:
            student.fname = encryptionHelper.decrypt(student.fname)
            student.lname = encryptionHelper.decrypt(student.lname)
            if student.mname:
                student.mname = encryptionHelper.decrypt(student.mname)
            else:
                student.mname = ""
            student.email = encryptionHelper.decrypt(student.email)
            required_students.append(student)
    for student in required_students:
        send_review_email(student, "Physique")


def send_review_email(student, form_type):
    todays_date = str(date.today())
    message = get_template(
        "student/email_template.html",
    ).render({"user": student.fname, "form_type": form_type})
    msg = EmailMessage(
        "Reminder to fill in your "
        + form_type
        + " Form, Dated: "
        + todays_date[8:]
        + "-"
        + todays_date[5:7]
        + "-"
        + todays_date[:4],
        message,
        settings.FROM_EMAIL_ID,
        [str(student.email)],
    )
    msg.content_subtype = "html"
    msg.send(fail_silently=True)
