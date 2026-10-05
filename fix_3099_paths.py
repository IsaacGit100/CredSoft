"""
One-off: fix any AccountModel rows whose code is '3099' but have an empty path
(depth wrong). Sets them to a sibling of 3010 in the capital root.
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CredSoft.settings")
django.setup()

from django_ledger.models import EntityModel, AccountModel
from django.db import connection

cursor = connection.cursor()
fixed = 0
skipped = 0
errors = []

for e in EntityModel.objects.all():
    coa = e.get_default_coa()
    if not coa:
        skipped += 1
        continue

    broken = AccountModel.objects.filter(coa_model=coa, code="3099", path="").first()
    if not broken:
        skipped += 1
        continue

    ref = AccountModel.objects.filter(coa_model=coa, code="3010").first()
    if not ref or not ref.path:
        errors.append(f"{e.slug}: no 3010 reference")
        continue

    prefix = ref.path[:-6]
    new_path = f"{prefix}000003"

    # avoid collision
    while AccountModel.objects.filter(coa_model=coa, path=new_path).exists():
        # bump the last 6 digits
        n = int(new_path[-6:]) + 1
        new_path = f"{prefix}{n:06d}"

    cursor.execute(
        "UPDATE django_ledger_accountmodel "
        "SET path = %s, depth = 3 "
        "WHERE code = '3099' AND coa_model_id = %s",
        [new_path, coa.pk.hex],
    )
    fixed += 1
    print(f"  + {e.slug} -> {new_path}")

print()
print(f"Fixed:   {fixed}")
print(f"Skipped: {skipped} (no broken 3099 or no COA)")
if errors:
    print("Errors:")
    for err in errors:
        print(f"  ! {err}")
