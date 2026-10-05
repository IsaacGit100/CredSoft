"""
Per-entity readiness snapshot.

For every EntityModel, compute:
    - entity_type     : Credit Union / Church / POS / …
    - has_coa         : ledger exists
    - has_config      : type-specific config exists
    - user_count      : users with this entity in allowed_entities or default
    - last_visit      : most recent last_login of those users
    - config_url      : where to fix the config (or None)
    - coa_url         : where to fix the COA (or None)
"""

from django.contrib.auth.models import User
from django.db.models import Max, Q
from django.urls import reverse, NoReverseMatch
from django_ledger.models import EntityModel

from django.db.models import Q
from CreditUnion.models import CreditUnionConfig


def _url(name, *args):
    try:
        return reverse(name, args=args) if args else reverse(name)
    except NoReverseMatch:
        return None


def _cu_config_check(entity):
   

    cu = getattr(entity, "cu_config", None)
    url = _url("CreditUnion:credit_union_config_edit", entity.slug)
    if cu is None:
        return False, "", url
    return (
        True,
        (f"Savings {cu.savings_interest_rate}%  Loans {cu.loan_interest_rate}%"),
        url,
    )


# Registry — add new entity types here as they gain their own config model
TYPE_CHECKS = {
    "credit_union": _cu_config_check,
  #  "church": _church_config_check,
  #  "pos":    _pos_config_check,
}


def entity_status_rows():
    rows = []

    for e in EntityModel.objects.select_related("config").all():
        cfg = getattr(e, "config", None)
        entity_type = cfg.entity_type if cfg else ""

        # --- COA check --- (unchanged)
        has_coa = False
        try:
            from django_ledger.models import LedgerModel

            has_coa = LedgerModel.objects.filter(entity=e).exists()
        except Exception:
            pass
        coa_url = _url("Tech:coa_management")

        # --- config check --- (unchanged)
        has_config, config_summary, config_url = False, "", _url("Tech:system_readiness")
        checker = TYPE_CHECKS.get(entity_type)
        if checker:
            has_config, config_summary, config_url = checker(e)

        # --- users with access (through UserProfile) ---
        user_qs = User.objects.filter(
            Q(djan_led_profile__allowed_entities=e)
            | Q(djan_led_profile__default_entity=e)
        ).distinct()
        user_count = user_qs.count()
        last_visit = user_qs.aggregate(m=Max("last_login"))["m"]


######

        # --- overall verdict ---
        if has_coa and has_config:
            status = "ok"
        elif has_coa or has_config:
            status = "warn"
        else:
            status = "fail"

        rows.append(
            {
                "entity": e,
                "type_code": entity_type,
                "type_label": (entity_type or "unknown").replace("_", " ").title(),
                "name": e.name,
                "slug": e.slug,
                "has_coa": has_coa,
                "has_config": has_config,
                "config_summary": config_summary,
                "user_count": user_count,
                "last_visit": last_visit,
                "config_url": config_url,
                "coa_url": coa_url,
                "status": status,
            }
        )

    return rows


def totals(rows):
    return {
        "total": len(rows),
        "ok": sum(1 for r in rows if r["status"] == "ok"),
        "warn": sum(1 for r in rows if r["status"] == "warn"),
        "fail": sum(1 for r in rows if r["status"] == "fail"),
        "coa_ok": sum(1 for r in rows if r["has_coa"]),
        "cfg_ok": sum(1 for r in rows if r["has_config"]),
        "users": sum(r["user_count"] for r in rows),
    }
