
import base64

import cv2
import numpy as np
import face_recognition

from openpyxl import Workbook
from .forms import EmployeeForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date

from .models import Employee, Attendance
from .services import recognize_face, refresh_face_cache


# =========================================================
# MAIN ATTENDANCE PAGE
# =========================================================

def dashboard(request):

    employees = Employee.objects.all()

    attendances = Attendance.objects.select_related(
        "employee"
    ).order_by("-detected_at")

    context = {
        "employees": employees,
        "attendances": attendances,
    }

    return render(
        request,
        "index.html",
        context
    )


# =========================================================
# FACE RECOGNITION
# =========================================================

def recognize(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "POST request required"
            },
            status=405
        )

    try:

        # =================================================
        # RECEIVE IMAGE
        # =================================================

        image_data = request.POST.get("image")

        if not image_data:

            return JsonResponse(
                {
                    "error": "No image received"
                },
                status=400
            )

        # Remove:
        # data:image/jpeg;base64,

        if "," in image_data:

            image_data = image_data.split(
                ",",
                1
            )[1]

        # =================================================
        # DECODE IMAGE
        # =================================================

        image_bytes = base64.b64decode(
            image_data
        )

        np_array = np.frombuffer(
            image_bytes,
            np.uint8
        )

        frame = cv2.imdecode(
            np_array,
            cv2.IMREAD_COLOR
        )

        if frame is None:

            return JsonResponse(
                {
                    "error": "Invalid image"
                },
                status=400
            )

        # =================================================
        # BGR → RGB
        # =================================================

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # =================================================
        # RESIZE FOR FASTER PROCESSING
        # =================================================

        scale = 0.5

        small_frame = cv2.resize(
            rgb_frame,
            (0, 0),
            fx=scale,
            fy=scale
        )

        # =================================================
        # DETECT FACES
        # =================================================

        face_locations = (
            face_recognition.face_locations(
                small_frame
            )
        )

        face_encodings = (
            face_recognition.face_encodings(
                small_frame,
                face_locations
            )
        )

        # =================================================
        # NO FACE
        # =================================================

        if not face_locations:

            return JsonResponse(
                {
                    "recognized": False,
                    "face_detected": False,
                    "faces": [],
                    "message": "No face detected"
                }
            )

        # =================================================
        # STORE ALL DETECTED FACES
        # =================================================

        detected_faces = []

        # =================================================
        # PROCESS EVERY FACE
        # =================================================

        for (
            location,
            face_encoding
        ) in zip(
            face_locations,
            face_encodings
        ):

            # -------------------------------------------------
            # ORIGINAL FACE COORDINATES
            # -------------------------------------------------

            top, right, bottom, left = location

            top = int(top / scale)
            right = int(right / scale)
            bottom = int(bottom / scale)
            left = int(left / scale)

            # =================================================
            # RECOGNIZE USING CACHE
            # =================================================

            employee = recognize_face(
                face_encoding
            )

            # =================================================
            # UNKNOWN FACE
            # =================================================

            if employee is None:

                detected_faces.append(
                    {
                        "top": top,
                        "right": right,
                        "bottom": bottom,
                        "left": left,

                        "recognized": False,

                        "name": "Unknown",

                        "designation": "",

                        "attendance_marked": False,

                        "already_marked": False,

                        "time": ""
                    }
                )

                continue

            # =================================================
            # RECOGNIZED EMPLOYEE
            # =================================================

            face_data = {

                "top": top,
                "right": right,
                "bottom": bottom,
                "left": left,

                "recognized": True,

                "name": employee.emp_name,

                "designation":
                    employee.designation,

                "attendance_marked": False,

                "already_marked": False,

                "time": ""

            }

            # =================================================
            # TODAY
            # =================================================

            today = timezone.localdate()

            # =================================================
            # CHECK ATTENDANCE
            # =================================================

            attendance = (
                Attendance.objects
                .filter(
                    employee=employee,
                    attendance_date=today
                )
                .first()
            )

            # =================================================
            # FIRST LOGIN
            # =================================================

            if attendance is None:

                attendance = (
                    Attendance.objects.create(
                        employee=employee,
                        attendance_date=today
                    )
                )

                face_data[
                    "attendance_marked"
                ] = True

            # =================================================
            # ALREADY MARKED
            # =================================================

            else:

                face_data[
                    "already_marked"
                ] = True

            # =================================================
            # FIRST LOGIN TIME
            # =================================================

            local_time = timezone.localtime(
                attendance.detected_at
            )

            face_data[
                "time"
            ] = local_time.strftime(
                "%I:%M:%S %p"
            )

            # =================================================
            # ADD FACE
            # =================================================

            detected_faces.append(
                face_data
            )

        # =================================================
        # RETURN ALL FACES
        # =================================================

        return JsonResponse(
            {
                "recognized": any(
                    face["recognized"]
                    for face in detected_faces
                ),

                "face_detected": True,

                "faces": detected_faces
            }
        )

    # =====================================================
    # ERROR
    # =====================================================

    except Exception as e:

        print(
            "Recognition error:",
            e
        )

        return JsonResponse(
            {
                "error": str(e)
            },
            status=500
        )


# =========================================================
# SUPERUSER DECORATOR
# =========================================================

def superuser_required(view_func):

    def wrapper(
        request,
        *args,
        **kwargs
    ):

        if not request.user.is_authenticated:

            return redirect(
                "admin_login"
            )

        if not request.user.is_superuser:

            return redirect(
                "admin_login"
            )

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper


# =========================================================
# ADMIN LOGIN
# =========================================================

def admin_login(request):

    if request.user.is_authenticated:

        if request.user.is_superuser:

            return redirect(
                "admin_dashboard"
            )

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            if user.is_superuser:

                login(
                    request,
                    user
                )

                return redirect(
                    "admin_dashboard"
                )

            return render(
                request,
                "admin_login.html",
                {
                    "error":
                        "Only superusers can "
                        "access the dashboard."
                }
            )

        return render(
            request,
            "admin_login.html",
            {
                "error":
                    "Invalid username or password."
            }
        )

    return render(
        request,
        "admin_login.html"
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@login_required
def admin_logout(request):

    logout(request)

    return redirect(
        "admin_login"
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

def get_filtered_attendances(request):
    attendance_search = request.GET.get("attendance_search", "").strip()
    date_from = parse_date(request.GET.get("date_from", ""))
    date_to = parse_date(request.GET.get("date_to", ""))

    attendances = Attendance.objects.select_related("employee")

    if attendance_search:
        attendances = attendances.filter(
            Q(employee__emp_code__icontains=attendance_search)
            | Q(employee__emp_name__icontains=attendance_search)
            | Q(employee__designation__icontains=attendance_search)
        )

    if date_from:
        attendances = attendances.filter(
            attendance_date__gte=date_from
        )

    if date_to:
        attendances = attendances.filter(
            attendance_date__lte=date_to
        )

    return attendances.order_by(
        "-attendance_date",
        "-detected_at"
    )


@superuser_required
def admin_dashboard(request):

    employee_search = request.GET.get(
        "employee_search",
        ""
    ).strip()

    employees = Employee.objects.all()

    if employee_search:
        employees = employees.filter(
            Q(emp_code__icontains=employee_search)
            | Q(emp_name__icontains=employee_search)
            | Q(designation__icontains=employee_search)
        )

    employees = employees.order_by("id")

    attendances = get_filtered_attendances(request)

    today = timezone.localdate()

    today_attendance = Attendance.objects.filter(
        attendance_date=today
    ).count()

    context = {
        "employees": employees,
        "attendances": attendances,
        "total_employees": Employee.objects.count(),
        "today_attendance": today_attendance,

        "employee_search": employee_search,

        "attendance_search": request.GET.get(
            "attendance_search",
            ""
        ).strip(),

        "date_from": request.GET.get(
            "date_from",
            ""
        ),

        "date_to": request.GET.get(
            "date_to",
            ""
        ),
    }

    return render(
        request,
        "admin_dashboard.html",
        context
    )



# =========================================================
# ADD EMPLOYEE
# =========================================================
@login_required
@superuser_required
def add_employee(request):

    if request.method == "POST":

        form = EmployeeForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            form.save()

            return redirect(
                "admin_dashboard"
            )

    else:

        form = EmployeeForm()

    return render(
        request,
        "employee_form.html",
        {
            "form": form,
            "title": "Add Employee"
        }
    )


# =========================================================
# EDIT EMPLOYEE
# =========================================================

@login_required
@superuser_required
def edit_employee(request, employee_id):

    employee = get_object_or_404(
        Employee,
        id=employee_id
    )

    if request.method == "POST":

        form = EmployeeForm(
            request.POST,
            request.FILES,
            instance=employee
        )

        if form.is_valid():

            form.save()

            return redirect(
                "admin_dashboard"
            )

    else:

        form = EmployeeForm(
            instance=employee
        )

    return render(
        request,
        "employee_form.html",
        {
            "form": form,
            "title": "Edit Employee"
        }
    )


# =========================================================
# DELETE EMPLOYEE
# =========================================================

@superuser_required
def delete_employee(
    request,
    employee_id
):

    employee = get_object_or_404(
        Employee,
        id=employee_id
    )

    employee.delete()

    # -----------------------------------------------------
    # Refresh recognition cache
    # -----------------------------------------------------

    refresh_face_cache()

    return redirect(
        "admin_dashboard"
    )


# =========================================================
# EXPORT ATTENDANCE EXCEL
# =========================================================

@superuser_required
def export_attendance_excel(request):

    attendances = get_filtered_attendances(request)

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Attendance"

    worksheet.append([
        "Employee ID",
        "Employee Code",
        "Employee Name",
        "Designation",
        "Attendance Date",
        "First Login Time"
    ])

    for attendance in attendances:

        local_time = timezone.localtime(
            attendance.detected_at
        )

        worksheet.append([
            attendance.employee.id,
            attendance.employee.emp_code,
            attendance.employee.emp_name,
            attendance.employee.designation,
            attendance.attendance_date.strftime(
                "%d-%m-%Y"
            ),
            local_time.strftime(
                "%I:%M:%S %p"
            )
        ])

    worksheet.column_dimensions["A"].width = 15
    worksheet.column_dimensions["B"].width = 20
    worksheet.column_dimensions["C"].width = 25
    worksheet.column_dimensions["D"].width = 25
    worksheet.column_dimensions["E"].width = 20
    worksheet.column_dimensions["F"].width = 20

    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="attendance.xlsx"'

    workbook.save(response)

    return response