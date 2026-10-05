"""
URL configuration for CredSoft project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("website.urls")),
    path("", include("djan_led.urls")),  # <-- Must be included
    path("dashboard/", include("core.urls")),  # Dashboard at /
    path("accounts/", include("django.contrib.auth.urls")),  # <-- Add this
    path("syssetup/", include("SysSetup.urls")),
    path("members/", include("MembersApp.urls")),
    path("users/", include("UserAuth.urls")),
    path("coa/", include("coa.urls")),
    path("loans/", include("LoanApp.urls")),
    path("recpay/", include("RecPayApp.urls")),
    #  path('finance/', include('FinanceApp.urls')),
    path("invest/", include("InvestApp.urls")),
    path("help/", include("help_module.urls")),
    path("coreapp/", include("CoreApp.urls")),
    path("supervisor/", include("Supervisor.urls")),
    path("loginapp/", include("LoginApp.urls")),
    path("services/", include("services.urls")),
    path("custom-reports/", include("CustomReports.urls")),
    path("backuprestore/", include("BackupRestore.urls", namespace="BackupRestore")),
    path("reset/", include("reset.urls", namespace="reset")),
    path("AndyApp/", include("AndyApp.urls")),
    # path('FixedAssets/', include('FixedAssets.urls')),
    path("finance/", include("FinanceApp.urls", namespace="FinanceApp")),
    path("fixed-assets/", include("FixedAssets.urls", namespace="FixedAssets")),
    path("opening-balances/", include("OpenBals.urls", namespace="OpenBals")),
    path("ledger/", include("django_ledger.urls", namespace="django_ledger")),
    #    path('django-ledger/', include('django_ledger.urls', namespace='django_ledger')),  # <-- ADD THIS
    path("finance/", views.finance_dashboard, name="finance_dashboard"),
    path("finance/switch-entity/<slug:slug>/", views.switch_entity, name="switch_entity"),
    path("church/", include("ChurchApp.urls", namespace="ChurchApp")),
    path("consolidated/", include("Consolidated.urls", namespace="Consolidated")),
    path("pos/", include("POS.urls", namespace="pos")),
    path("CreditUnion/", include("CreditUnion.urls", namespace="CreditUnion")),
    path("Dividend", include("Dividend.urls", namespace="Dividend")),
    path("Tech", include("Tech.urls", namespace="Tech")),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("docs/", include("DocMgt.urls", namespace="DocMgt")),
    path("images/", include("Images.urls", namespace="Images")),
    path("Report/", include("Report.urls", namespace="Report")),
]


# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


