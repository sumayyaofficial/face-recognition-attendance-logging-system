from django.db import models

# Create your models here.

class Employee(models.Model):
    emp_code = models.CharField(max_length=20)
    emp_name = models.CharField(max_length=50)
    designation = models.CharField(max_length=100)
    emp_dob = models.DateField()
    emp_place = models.CharField(max_length=100)
    emp_phone = models.CharField(max_length=10)
    emp_image = models.ImageField(upload_to='documents',null=True)

    class Meta:
        db_table = "employee_table"

class Attendance(models.Model):

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE
    )

    attendance_date = models.DateField()

    detected_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "employee",
                    "attendance_date"
                ],

                name="unique_employee_attendance_per_day"
            )

        ]

        ordering = [
            "-detected_at"
        ]

    def __str__(self):

        return (
            f"{self.employee.emp_name} - "
            f"{self.attendance_date}"
        )