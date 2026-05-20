from django.apps import AppConfig

class ServiceuserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'serviceuser'

    def ready(self):
        # The dot (.) means "this current folder"
        from . import signals