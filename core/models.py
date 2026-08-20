from django.db import models

# Create your models here.
from django.db import models


class PermissionHolder(models.Model):
    class Meta:
        managed = False
        permissions = [
            ("can_view_user_management", "Can view user management"),
            ("can_manage_users", "Can add, edit, delete users"),
            ("can_view_backup", "Can access backup and restore"),
            ("can_perform_factory_reset", "Can perform factory reset"),
            ("can_view_reports", "Can view financial reports"),
            # add as needed
        ]



