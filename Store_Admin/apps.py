from django.apps import AppConfig

class StoreAdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Store_Admin'

    def ready(self):
        import Store_Admin.signals  # ✅ Ensure signals are imported
