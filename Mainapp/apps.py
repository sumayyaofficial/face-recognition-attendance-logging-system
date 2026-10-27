from django.apps import AppConfig


class MainappConfig(AppConfig):

    default_auto_field = "django.db.models.BigAutoField"

    name = "Mainapp"

    def ready(self):

        import Mainapp.signals

        from .services import refresh_face_cache

        refresh_face_cache()