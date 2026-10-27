import cv2
import face_recognition
import numpy as np


def eye_aspect_ratio(eye):

    # Convert the eye landmark points
    # into numpy array

    points = np.array(eye)


    # Vertical distances

    vertical_1 = np.linalg.norm(
        points[1] - points[5]
    )

    vertical_2 = np.linalg.norm(
        points[2] - points[4]
    )


    # Horizontal distance

    horizontal = np.linalg.norm(
        points[0] - points[3]
    )


    if horizontal == 0:

        return 0


    ear = (
        vertical_1 + vertical_2
    ) / (2.0 * horizontal)


    return ear


def check_blink(frames):

    """
    frames = list of RGB images

    Returns:

        True  -> blink detected
        False -> no blink
    """


    if len(frames) < 5:

        return False


    ear_values = []


    for frame in frames:

        try:

            # Detect face

            face_locations = (
                face_recognition.face_locations(
                    frame
                )
            )


            if not face_locations:

                continue


            # Get facial landmarks

            landmarks = (
                face_recognition.face_landmarks(
                    frame,
                    face_locations
                )
            )


            if not landmarks:

                continue


            face_landmark = landmarks[0]


            # Both eyes

            left_eye = face_landmark.get(
                "left_eye"
            )

            right_eye = face_landmark.get(
                "right_eye"
            )


            if not left_eye or not right_eye:

                continue


            left_ear = eye_aspect_ratio(
                left_eye
            )

            right_ear = eye_aspect_ratio(
                right_eye
            )


            average_ear = (
                left_ear + right_ear
            ) / 2.0


            ear_values.append(
                average_ear
            )


        except Exception:

            continue


    if len(ear_values) < 3:

        return False


    # -------------------------------
    # BLINK DETECTION
    # -------------------------------
    #
    # Open eye:
    # approximately > 0.20
    #
    # Closed eye:
    # approximately < 0.18
    #
    # We look for:
    #
    # OPEN → CLOSED → OPEN
    #
    # -------------------------------

    closed_threshold = 0.18

    open_threshold = 0.21


    was_open = False

    was_closed = False


    for ear in ear_values:

        # Eye is open

        if ear >= open_threshold:

            if was_closed:

                # CLOSED → OPEN
                # means blink completed

                return True


            was_open = True


        # Eye is closed

        elif ear < closed_threshold:

            if was_open:

                was_closed = True


    return False