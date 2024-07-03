from django.urls import path
from accounts import views_other
from accounts import views_registration
from accounts import views_password
from accounts import views_moduleOne
from accounts import views_physique
from accounts import views_supercoordinator
from accounts import views_coordinator
from accounts import views_teacher
from accounts import views_parent
from accounts import views_student

app_name = "accounts"

urlpatterns = [
    path("forbidden/", views_other.forbidden, name="forbidden"),
    path("already_filled/", views_other.already_filled, name="already_filled"),
    path("form_closed/", views_other.form_closed, name="form_closed"),
    path("", views_registration.root, name="root"),
    path("login/", views_registration.loginU, name="loginlink"),
    path("logout/", views_registration.logoutU, name="logoutu"),
    path("registration/", views_registration.registration, name="registration"),
    path("consent/", views_registration.consent, name="consent"),
    path("consent_adult/", views_registration.consent_adult, name="consent_adult"),
    path("parents_info/", views_registration.parents_info, name="parents_info"),
    path("students_info/", views_registration.students_info, name="students_info"),
    path(
        "students_info_adult/",
        views_registration.students_info_adult,
        name="students_info_adult",
    ),
    path("give_consent/", views_registration.give_consent, name="give_consent"),
    path("ask_to_give_consent/", views_registration.ask_to_give_consent, name="ask_to_give_consent"),
    path(
        "addSuperCoordinatorForm/",
        views_registration.addSuperCoordinatorForm,
        name="add_supercoordinator_form",
    ),
    path("forgot_password/", views_password.forgot_password, name="forgot_password"),
    path(
        "forgot_password/<uidb64>/<token>/",
        views_password.forgot_password_final,
        name="forgot_password_final",
    ),
    path(
        "forgot_password/questions/",
        views_password.forgot_password_questions,
        name="forgot_password_questions",
    ),
    path("change_password/", views_password.change_password, name="change_password"),
    path(
        "view_supercoordinator_profile/",
        views_supercoordinator.view_supercoordinator_profile,
        name="view_supercoordinator_profile",
    ),
    path(
        "edit_supercoordinator_profile/",
        views_supercoordinator.edit_supercoordinator_profile,
        name="edit_supercoordinator_profile",
    ),
    path(
        "view_coordinator_profile/",
        views_coordinator.view_coordinator_profile,
        name="view_coordinator_profile",
    ),
    path(
        "edit_coordinator_profile/",
        views_coordinator.edit_coordinator_profile,
        name="edit_coordinator_profile",
    ),
    path(
        "view_teacher_profile/",
        views_teacher.view_teacher_profile,
        name="view_teacher_profile",
    ),
    path(
        "edit_teacher_profile/",
        views_teacher.edit_teacher_profile,
        name="edit_teacher_profile",
    ),
    path(
        "view_parent_profile/",
        views_parent.view_parent_profile,
        name="view_parent_profile",
    ),
    path(
        "edit_parent_profile/",
        views_parent.edit_parent_profile,
        name="edit_parent_profile",
    ),
    path(
        "view_student_profile/",
        views_student.view_student_profile,
        name="view_student_profile",
    ),
    path(
        "edit_student_profile/",
        views_student.edit_student_profile,
        name="edit_student_profile",
    ),
    path("password_changed/", views_password.password_changed, name="password_changed"),
    path("draft/", views_moduleOne.draft, name="draft"),
    path("previous/", views_moduleOne.previous, name="previous"),
    path("moduleOne/", views_moduleOne.moduleOne, name="module_one"),
    path("moduleOne-2/", views_moduleOne.moduleOne2, name="module_one_2"),
    path("moduleOne-3/", views_moduleOne.moduleOne3, name="module_one_3"),
    path(
        "parent_dashboard/<int:id>/moduleOne",
        views_moduleOne.parentModuleOne,
        name="parentModuleOne",
    ),
    path(
        "parent_dashboard/<int:id>/moduleOne-2",
        views_moduleOne.parentModuleOne2,
        name="parentsModuleOne2",
    ),
    path(
        "parent_dashboard/<int:id>/moduleOne-3",
        views_moduleOne.parentModuleOne3,
        name="parentsModuleOne3",
    ),
    path("physiquedraft/", views_physique.physiqueDraft, name="physiquedraft"),
    path("physique/", views_physique.physique, name="physique"),
    path(
        "parent_dashboard/<int:id>/physique",
        views_physique.parentPhysique,
        name="parentPhysique",
    ),
    path(
        "supercoordinator_dashboard/",
        views_supercoordinator.supercoordinator_dashboard,
        name="supercoordinator_dashboard",
    ),
    path(
        "addOrganizationForm/",
        views_supercoordinator.addOrganizationForm,
        name="add_organization_form",
    ),
    path(
        "view_coordinators/<int:id>/",
        views_supercoordinator.viewCoordinators,
        name="view_coordinators",
    ),
    path(
        "addCoordinatorForm/<int:id>/",
        views_supercoordinator.addCoordinatorForm,
        name="add_coordinator_form",
    ),
    path(
        "all_coordinators/",
        views_supercoordinator.allCoordinators,
        name="all_coordinators",
    ),
    path(
        "supercoordinator_reset_password/",
        views_supercoordinator.supercoordinator_reset_password,
        name="supercoordinator_reset_password",
    ),
    path(
        "coordinators_data_download/",
        views_supercoordinator.coordinators_data_download,
        name="coordinators_data_download",
    ),
    path(
        "coordinator_dashboard/",
        views_coordinator.coordinator_dashboard,
        name="coordinator_dashboard",
    ),
    path("addTeacherForm/", views_coordinator.addTeacherForm, name="add_teacher_form"),
    path("all_sessions/", views_coordinator.allSessions, name="all_sessions"),
    path("addSessionForm/", views_coordinator.addSessionForm, name="add_session_form"),
    path(
        "view_session_teachers/<int:id>/<int:open_id>/",
        views_coordinator.viewSessionTeachers,
        name="view_session_teachers",
    ),
    path(
        "switch_teachers_list/<int:id>/<int:teacher_id>/",
        views_coordinator.switchTeachersList,
        name="switch_teachers_list",
    ),
    path(
        "switch_coordinators_list/<int:coord_id>/<int:page_id>/",
        views_supercoordinator.switchCoordinatorsList,
        name="switch_coordinators_list",
    ),
    path(
        "switch_teacher_user_list/<int:teacher_id>/",
        views_coordinator.switchTeachersUserList,
        name="switch_teacher_user_list",
    ),
    path(
        "get_session_teachers_template/",
        views_coordinator.getSessionTeachersTemplate,
        name="get_session_teachers_template",
    ),
    path(
        "add_session_teachers/<int:id>/",
        views_coordinator.addSessionTeachers,
        name="add_session_teachers",
    ),
    path(
        "add_session_teachers_list/<int:id>/",
        views_coordinator.addSessionTeachersList,
        name="add_session_teachers_list",
    ),
    path(
        "remove_session_teacher/<int:session_id>/<int:teacher_id>/",
        views_coordinator.removeSessionTeacher,
        name="remove_session_teacher",
    ),
    path(
        "remove_coordinator/<int:coord_id>/<int:page_id>/",
        views_supercoordinator.removeCoordinator,
        name="remove_coordinator",
    ),
    path(
        "remove_teacher/<int:teacher_id>/",
        views_coordinator.removeTeacher,
        name="remove_teacher",
    ),
    path(
        "coordinator_reset_password/",
        views_coordinator.coordinator_reset_password,
        name="coordinator_reset_password",
    ),
    path(
        "teachers_data_download/",
        views_coordinator.teachers_data_download,
        name="teachers_data_download",
    ),
    path(
        "parents_and_students_data_download/",
        views_coordinator.parents_and_students_data_download,
        name="parents_and_students_data_download",
    ),
    path(
        "teacher_all_sessions/",
        views_teacher.teacherAllSessions,
        name="teacher_all_sessions",
    ),
    path(
        "view_session_students/<int:id>/<int:open_id>/",
        views_teacher.viewSessionStudents,
        name="view_session_students",
    ),
    path(
        "get_session_students_template/",
        views_teacher.getSessionStudentsTemplate,
        name="get_session_students_template",
    ),
    path(
        "add_session_students/<int:id>/",
        views_teacher.addSessionStudents,
        name="add_session_students",
    ),
    path(
        "add_session_students_list/<int:id>/",
        views_teacher.addSessionStudentsList,
        name="add_session_students_list",
    ),
    path(
        "remove_session_student/<int:session_id>/<int:student_id>/",
        views_teacher.removeSessionStudent,
        name="remove_session_student",
    ),
    path(
        "view_session_forms/<int:id>/",
        views_teacher.viewSessionForms,
        name="view_session_forms",
    ),
    path(
        "teacher_dashboard/<int:id>/<int:session_id>/<int:form_type>/",
        views_teacher.getFormDetails,
        name="get_form_details",
    ),
    
    path("manage-forms/<int:id>/", views_teacher.manageForms, name="manage_forms"),
    path("getTemplate/", views_teacher.getTemplate, name="get_template"),
    path("bulkRegister/", views_teacher.bulkRegister, name="bulk_register"),
    path("parent_dashboard/", views_parent.parent_dashboard, name="parent_dashboard"),
    path("addStudentForm/", views_parent.addStudentForm, name="add_student_form"),
    path(
        "parent_dashboard/<int:id>/",
        views_parent.showStudent,
        name="parent_dashboard_student",
    ),
    path(
        "student_dashboard/", views_student.student_dashboard, name="student_dashboard"
    ),
    path(
        "secondary_registration/",
        views_student.secondary_registration,
        name="secondary_registration",
    ),
]
