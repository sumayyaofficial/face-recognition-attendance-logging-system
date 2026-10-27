"""
URL configuration for faceapp project.

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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from Mainapp import views
urlpatterns = [
    path("admin/", admin.site.urls),
    path("",views.dashboard,name="dashboard"),
    path(
        "recognize/",
        views.recognize,
        name="recognize"
    ),
    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),


    # Employee management

    path(
        "admin-dashboard/employees/add/",
        views.add_employee,
        name="add_employee"
    ),

    path(
        "admin-dashboard/employees/<int:employee_id>/edit/",
        views.edit_employee,
        name="edit_employee"
    ),

    path(
        "admin-dashboard/employees/<int:employee_id>/delete/",
        views.delete_employee,
        name="delete_employee"
    ),


    # Excel

    path(
        "admin-dashboard/attendance/export/",
        views.export_attendance_excel,
        name="export_attendance_excel"
    ),

    path(
        "admin-login/",
        views.admin_login,
        name="admin_login"
    ),

    path(
        "admin-logout/",
        views.admin_logout,
        name="admin_logout"
    ),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)