from django.contrib import admin
from .models import *

class AccountsAdminArea(admin.AdminSite):
    site_header = "Accounts Admin Area"


accounts_admin_area = AccountsAdminArea(name="accounts_admin")

accounts_admin_area.register(Occupation)
accounts_admin_area.register(FamilyType)
accounts_admin_area.register(ReligiousBelief)
accounts_admin_area.register(Education)
accounts_admin_area.register(OrganizationTypes)
accounts_admin_area.register(FamilyIncome)
accounts_admin_area.register(RationCardColor)
accounts_admin_area.register(Form)