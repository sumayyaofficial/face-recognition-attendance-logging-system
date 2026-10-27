from django.db.models.signals import (
    post_save,
    post_delete
)

from django.dispatch import receiver

from .models import Employee

from .services import refresh_face_cache


# =========================================================
# EMPLOYEE ADDED / UPDATED
# =========================================================

@receiver(post_save, sender=Employee)
def employee_saved(
    sender,
    instance,
    created,
    **kwargs
):

    print(
        f"Employee saved: "
        f"{instance.emp_name}"
    )

    refresh_face_cache()


# =========================================================
# EMPLOYEE DELETED
# =========================================================

@receiver(post_delete, sender=Employee)
def employee_deleted(
    sender,
    instance,
    **kwargs
):

    print(
        f"Employee deleted: "
        f"{instance.emp_name}"
    )

    refresh_face_cache()