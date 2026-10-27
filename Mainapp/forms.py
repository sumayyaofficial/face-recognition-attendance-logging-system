from django import forms
from .models import Employee


class EmployeeForm(forms.ModelForm):

    class Meta:

        model = Employee

        fields = [
            "emp_code",
            "emp_name",
            "designation",
            "emp_dob",
            "emp_place",
            "emp_phone",
            "emp_image",
        ]

        widgets = {

            "emp_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Employee Code"
                }
            ),

            "emp_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Employee Name"
                }
            ),

            "designation": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Designation"
                }
            ),

            "emp_dob": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "emp_place": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Place"
                }
            ),

            "emp_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Phone Number"
                }
            ),

            "emp_image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*"
                }
            ),
        }