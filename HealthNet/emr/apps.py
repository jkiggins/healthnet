from django.apps import AppConfig

class EmrConfig(AppConfig):
    name = 'emr'

    def ready(self):
        import emr.signals
