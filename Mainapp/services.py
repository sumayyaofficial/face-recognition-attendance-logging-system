import os
import threading

import face_recognition
import numpy as np

from .models import Employee


# =========================================================
# FACE RECOGNITION CACHE
# =========================================================

_known_encodings = []
_known_employees = []

_cache_lock = threading.Lock()


# =========================================================
# LOAD ALL EMPLOYEE FACES
# =========================================================

def refresh_face_cache():

    global _known_encodings
    global _known_employees

    new_encodings = []
    new_employees = []

    print("\n========================================")
    print("Refreshing face recognition cache...")
    print("========================================")

    employees = Employee.objects.all()

    for employee in employees:

        # -----------------------------------------
        # Employee must have an image
        # -----------------------------------------

        if not employee.emp_image:
            print(
                f"Skipping {employee.emp_name}: "
                f"No image"
            )
            continue

        try:

            image_path = employee.emp_image.path

            # -----------------------------------------
            # Check image exists
            # -----------------------------------------

            if not os.path.exists(image_path):

                print(
                    f"Skipping {employee.emp_name}: "
                    f"Image not found"
                )

                continue

            # -----------------------------------------
            # Load image
            # -----------------------------------------

            image = face_recognition.load_image_file(
                image_path
            )

            # -----------------------------------------
            # Generate face encoding
            # -----------------------------------------

            face_encodings = (
                face_recognition.face_encodings(
                    image
                )
            )

            if not face_encodings:

                print(
                    f"Skipping {employee.emp_name}: "
                    f"No face found"
                )

                continue

            # -----------------------------------------
            # Use first detected face
            # -----------------------------------------

            encoding = face_encodings[0]

            new_encodings.append(
                encoding
            )

            new_employees.append(
                employee
            )

            print(
                f"Loaded face: "
                f"{employee.emp_name}"
            )

        except Exception as e:

            print(
                f"Error loading "
                f"{employee.emp_name}: {e}"
            )

    # =================================================
    # ATOMICALLY UPDATE CACHE
    # =================================================

    with _cache_lock:

        _known_encodings = new_encodings

        _known_employees = new_employees

    print(
        f"Total employee faces loaded: "
        f"{len(_known_employees)}"
    )

    print("========================================\n")


# =========================================================
# GET CURRENT CACHE
# =========================================================

def get_face_cache():

    with _cache_lock:

        return (
            _known_encodings.copy(),
            _known_employees.copy()
        )


# =========================================================
# RECOGNIZE FACE
# =========================================================

def recognize_face(face_encoding):

    known_encodings, employees = (
        get_face_cache()
    )

    if not known_encodings:

        return None

    # -----------------------------------------
    # Compare face
    # -----------------------------------------

    matches = face_recognition.compare_faces(
        known_encodings,
        face_encoding,
        tolerance=0.50
    )

    # -----------------------------------------
    # Calculate distances
    # -----------------------------------------

    face_distances = (
        face_recognition.face_distance(
            known_encodings,
            face_encoding
        )
    )

    if len(face_distances) == 0:

        return None

    # -----------------------------------------
    # Best match
    # -----------------------------------------

    best_match_index = np.argmin(
        face_distances
    )

    best_distance = (
        face_distances[best_match_index]
    )

    print(
        f"Best distance: "
        f"{best_distance:.4f}"
    )

    # -----------------------------------------
    # Check tolerance
    # -----------------------------------------

    if matches[best_match_index]:

        employee = employees[
            best_match_index
        ]

        print(
            f"Recognized: "
            f"{employee.emp_name}"
        )

        return employee

    print("Unknown face")

    return None