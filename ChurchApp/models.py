# Create your models here.
from django.db import models

# Create your models here. / ChurchApp/models.py

from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import choices
from django_ledger.models import (EntityModel, JournalEntryModel, TransactionModel, AccountModel)


from django.utils import timezone
from django.contrib.auth import get_user_model

class Role(models.Model):
    """
    Predefined roles that members can hold.
    """
    ROLE_TYPES = [
        ("Officiant", "Officiant"),
        ("Usher", "Usher"),
        ("Verger", "Verger"),
        ("PCC", "PCC"),
        ("Chalice-Assistant", "Chalice-Assistant"),
        ("Priest-Warden", "Priest Warden"),
        ("Peoples-Warden", "People's Warden"),
        ("Accounts-Clerk", "Accounts-Clerk"),
        ("Parish-Clerk", "Parish-Clerk"),
        ('other', 'Other'),
    ]

    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=50, choices=ROLE_TYPES)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
            constraints = [
            models.UniqueConstraint(
                fields=['entity', 'name'],
                name='unique_role_per_entity'
            )
        ]

    def __str__(self):
        return self.display_name

class Member(models.Model):

    ROLE_CHOICES = [
        ("Accounts", "Accounts"),
        ("Parish-Clerk", "Parish Clerk"),
        ("Security", "Security"),
        ("ChapelKeeper", "ChapelKeeper"),
        ("Choirmaster", "Choirmaster"),
        ("Organist", "Organist"),
        ("Other", "Other"),
    ]

    TITLE_CHOICES = [
        ('MR', 'Mr.'),
        ('MRS', 'Mrs.'),
        ('MS', 'Ms.'),
        ('DR', 'Dr.'),
        ("Rev.", "Rev."),
        ("Fr.", "Fr."),
        ("Canon", "Canon"),
        ("Archdeacon", "Archdeacon"),
        ("Dean", "Dean"),
        ("Bishop", "Bishop"),
        ("ArchBishop", "ArchBishop"),
    ]

    EDUCATION_CHOICES = [
        ("None", "None"),
        ("Basic", "Basic"),
        ("SHS", "SHS"),
        ("1st Degree", "1st Degree"),
        ("2nd Degree", "2nd Degree"),
        ("PHD", "PHD"),
        ("Professional", "Professional"),
    ]

    RELIGION_CHOICES = [
        ("Christian", "Christian"),
        ("Moslem", "Moslem"),
    ]
    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name="members")
    # Personal details
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True, default="")
    other_names = models.CharField(max_length=100, null=True, blank=True, default="")
    last_name = models.CharField(max_length=100, null=True, blank=True, default="")
    full_name = models.CharField(max_length=200, null=True, blank=True, default="")
    email = models.EmailField(blank=True, null=True, default="")
    telephone1 = models.CharField(max_length=20, null=True, blank=True, default="")
    telephone2 = models.CharField(max_length=20, null=True, blank=True, default="")
    postal_address = models.CharField(max_length=150, null=True, blank=True, default="")
    res_address = models.CharField(max_length=150, null=True, blank=True, default="")
    near_landmark = models.CharField(max_length=100, null=True, blank=True, default="")
    education_level = models.CharField(max_length=50, null=True, blank=True, choices=EDUCATION_CHOICES, default="")
    profession = models.CharField(max_length=100, blank=True, default="")
    ghana_card_no = models.CharField(max_length=15, null=True, default="", blank=True)
    passport_picture = models.ImageField(
        upload_to="church_members/passports/",
        blank=True,
        null=True,
        help_text="Passport-size photograph of the member.",
    )

    date_of_birth = models.DateField(default=None, null=True, blank=True)
    date_baptised = models.DateField(default=None, null=True, blank=True)
    date_confirmed = models.DateField(default=None, null=True, blank=True)
    date_enrolled = models.DateField(default=None, null=True, blank=True)
    date_expired = models.DateField(default=None, null=True, blank=True)

    guild_first = models.CharField(max_length=120, null=True, blank=True, default="")   # select from guilds model
    guild_second = models.CharField(max_length=120, null=True, blank=True, default="")  # select from guilds model
    guild_third = models.CharField(max_length=120, null=True, blank=True, default="")  # select from guilds model

    no_of_children = models.IntegerField(default=0, null=True, blank=True)
    names_of_children = models.JSONField(default=list, blank=True)  # List of children's names
    # Office information
    office_name = models.CharField(max_length=150, null=True, blank=True, default="")
    office_address = models.CharField(max_length=100, null=True, blank=True, default="")
    office_res_address = models.CharField(max_length=120, null=True, blank=True, default="")
    office_phone = models.CharField(max_length=150, null=True, blank=True, default="")
    office_email = models.EmailField(blank=True, null=True, default="")
    nature_of_business = models.CharField(max_length=150, null=True, blank=True, default="")

    # Spouse information (corrected duplicate fields)
    spouse_title = models.CharField(max_length=20, choices=TITLE_CHOICES, blank=True, null=True)
    spouse_name = models.CharField(max_length=100, blank=True, null=True, default="")
    spouse_postal_address = models.CharField(max_length=100, null=True, blank=True, default="")
    spouse_email_address = models.EmailField(blank=True, null=True, default="")
    spouse_telephone = models.CharField(max_length=20, null=True, blank=True, default="") 
    spouse_company_name = models.CharField(max_length=150, null=True, blank=True, default="")
    spouse_res_address = models.CharField(max_length=150, null=True, blank=True, default="")
    spouse_religion = models.CharField(
        max_length=150, choices=RELIGION_CHOICES, null=True, blank=True, default=""
    )
    spouse_occupation = models.CharField(max_length=100, null=True, blank=True, default="")
    spouse_education_level = models.CharField(
        max_length=120, choices=EDUCATION_CHOICES, null=True,    blank=True, default=""
    )
    spouse_date_of_birth = models.DateField(default=None, null=True, blank=True)
    spouse_near_landmark = models.CharField(
        max_length=100, null=True, blank=True, default=""
    )
    spouse_church = models.CharField(max_length=100, null=True, blank=True, default="")

    father_name = models.CharField(max_length=100, null=True, blank=True, default="")
    father_res_address = models.CharField(max_length=100, null=True, blank=True, default="")
    father_telephone = models.CharField(max_length=15, null=True, blank=True, default="")
    father_deceased = models.BooleanField(default=False)

    mother_name = models.CharField(max_length=100, null=True, blank=True, default="")
    mother_res_address = models.CharField(max_length=100, null=True, blank=True, default="")
    mother_telephone = models.CharField(max_length=15, null=True, blank=True, default="")
    mother_deceased = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False, help_text="Soft delete flag")
    tot_tithe = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    tot_dues = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    tot_special_offering = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)       

    # Optional: link to shared entity
    # entity = models.ForeignKey('core.Entity', on_delete=models.CASCADE, default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    roles = models.ManyToManyField(Role, through='MemberRole', related_name='members', blank=True)


    def __str__(self):
        return self.full_name or f"{self.last_name} {self.first_name} {self.other_names}"
        """Return the full name of the member"""


    # Helper methods
    def has_role(self, role_name):
        """Check if member has a specific role."""
        return self.member_roles.filter(role__name=role_name, is_active=True).exists()

    def get_roles(self):
        """Get all active roles as a list."""
        return self.member_roles.filter(is_active=True).select_related('role')

    def get_role_names(self):
        """Get active role names as a list of strings."""
        return [mr.role.display_name for mr in self.get_roles()]

    def save(self, *args, **kwargs):
        name_parts = filter(None, [self.first_name, self.other_names, self.last_name])
        self.full_name = " ".join(name_parts).strip()
        super().save(*args, **kwargs)

class Clergy(models.Model):
    TITLE_CHOICES = [
        ("Fr.", "Fr."),
        ("Can.", "Can."),
        ("Ven.", "Ven."),
        ("Bishop", "Bishop"),
    ]
    CLERGY_TYPES = [
        ("parish_priest", "Parish Priest"),
        ("assistant", "Assisting Priest"),
        ("visitor", "Visiting Priest"),
    ]
    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name="clergy")
    clergy_type = models.CharField(max_length=30, choices=CLERGY_TYPES, default="assistant")
    title = models.CharField(max_length=20, blank=True, null=True, choices=TITLE_CHOICES, default='Fr.')
    first_name = models.CharField(max_length=100, blank=True, default="")
    other_names = models.CharField(max_length=50, blank=True, default="")
    last_name = models.CharField(max_length=100, blank=True, default="")
    full_name = models.CharField(max_length=200, blank=True)
    email_address = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20)
    postal_address = models.CharField(max_length=150, blank=True, default="")
    res_address = models.CharField(max_length=150, blank=True, default="")
    date_arrived = models.DateField(null=True, blank=True, default=None)
    date_depart = models.DateField(null=True, blank=True, default=None)

    def __str__(self):
        return self.last_name

    def save(self, *args, **kwargs):
        name_parts = filter(None, [self.first_name, self.other_names, self.last_name])
        self.full_name = " ".join(name_parts).strip()
        super().save(*args, **kwargs)


class Service(models.Model):
    DAY_ORDER = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]

    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name="services")
    date = models.DateField()
    name_of_service = models.CharField(max_length=100, null=True, blank=True, default="Sunday Service")
    # -------------VARIABLE SERVICE PARTICIPANTS------------------------------------
    clergy = models.ManyToManyField("Clergy", blank=True, related_name="services")
    officiant = models.ForeignKey("Member", on_delete=models.SET_NULL, null=True, blank=True, related_name="officiated_services")
    ushers = models.ManyToManyField("Member", blank=True, related_name="ushered_services")
    chalice_assistants = models.ManyToManyField("Member", blank=True, related_name="chalice_assisted_services")
    # --------------FIXED OFFICE HOLDERS -----------------------------------
    priest_warden = models.CharField(max_length=200, blank=True, default="")
    peoples_warden = models.CharField(max_length=200, blank=True, default="")
    verger = models.CharField(max_length=200, blank=True, default="")
    parish_clerk = models.CharField(max_length=200, blank=True, default="")
    accounts_clerk = models.CharField(max_length=200, blank=True, default="")
    pcc_members = models.JSONField(default=list, blank=True)
    # -------------EXISTING FINANCIAL FIELDS------------------------------------

    attendance = models.PositiveIntegerField(default=0)
    communicants = models.PositiveIntegerField(default=0)
    general_offertory = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    dues = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    tithes = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    day_born_offerings = models.JSONField(default=dict, blank=True)
    guild_offerings = models.JSONField(default=list, blank=True)
    special_thank_offering = models.JSONField(default=list, blank=True)
    easter_offering = models.JSONField(default=list, blank=True)
    christmas_offering = models.JSONField(default=list, blank=True)

    harvest_offering = models.JSONField(default=list, blank=True)
    other_collections = models.JSONField(default=list, blank=True)
    day_born_total = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    guild_total = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    special_total = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    trans = models.ForeignKey("RecPayApp.Trans", on_delete=models.SET_NULL, null=True, blank=True, related_name="service_activities")
    posted_to_ledger = models.BooleanField(default=False)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    journal_entry_id = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.name_of_service} - {self.date}"      

    def calculate_totals(self):
        """Calculate all Service offering totals using Decimal values."""

        def to_decimal(value):
            if value is None or value == "":
                return Decimal("0")
            try:
                return Decimal(str(value).replace(",", ""))
            except (TypeError, ValueError, ArithmeticError):
                return Decimal("0")

        # Day Born total
        if isinstance(self.day_born_offerings, dict):
            self.day_born_total = sum(
                (to_decimal(amount) for amount in self.day_born_offerings.values()),
                Decimal("0"),
            )
        else:
            self.day_born_total = Decimal("0")

        # Guild total
        if isinstance(self.guild_offerings, list):
            self.guild_total = sum(
                (
                    to_decimal(item.get("amount", 0))
                    for item in self.guild_offerings
                    if isinstance(item, dict)
                ),
                Decimal("0"),
            )
        else:
            self.guild_total = Decimal("0")

        # Special / seasonal offerings
        specials = [
            self.special_thank_offering,
            self.harvest_offering,
            self.christmas_offering,
            self.easter_offering,
            self.other_collections,
        ]

        self.special_total = Decimal("0")

        for special_list in specials:
            if isinstance(special_list, list):
                self.special_total += sum(
                    (
                        to_decimal(item.get("amount", 0))
                        for item in special_list
                        if isinstance(item, dict)
                    ),
                    Decimal("0"),
                )

        # Grand total
        self.grand_total = (
            to_decimal(self.general_offertory)
            + to_decimal(self.dues)
            + to_decimal(self.tithes)
            + self.day_born_total
            + self.guild_total
            + self.special_total
        )

    def save(self, *args, **kwargs):
        self.calculate_totals()
        super().save(*args, **kwargs)

    @staticmethod
    def _json_list_total(items):
        def to_decimal(value):
            if value is None or value == "":
                return Decimal("0")

            try:
                return Decimal(str(value).replace(",", ""))
            except (TypeError, ValueError, ArithmeticError):
                return Decimal("0")

        if not isinstance(items, list):
            return Decimal("0")

        return sum(
            (
                to_decimal(item.get("amount", 0))
                for item in items
                if isinstance(item, dict)
            ),
            Decimal("0"),
        )

    @property
    def guild_tot(self):
        return self._json_list_total(self.guild_offerings)

    @property
    def easter_total(self):
        return self._json_list_total(self.easter_offering)

    @property
    def christmas_total(self):
        return self._json_list_total(self.christmas_offering)

    @property
    def harvest_total(self):
        return self._json_list_total(self.harvest_offering)

    @property
    def special_thank_offering_total(self):
        return self._json_list_total(self.special_thank_offering)

    @property
    def other_collections_total(self):
        return self._json_list_total(self.other_collections)

    @property
    def ordered_day_born_offerings(self):
        return [
            (day, self.day_born_offerings.get(day, 0))
            for day in self.DAY_ORDER
            if day in self.day_born_offerings
        ]

User = get_user_model()


class Event(models.Model):
    EVENT_TYPES = [
        ("service", "Church Service"),
        ("bible_study", "Bible Study"),
        ("prayer_meeting", "Prayer Meeting"),
        ("youth", "Youth Meeting"),
        ("children", "Children's Church"),
        ("choir", "Choir Practice"),
        ("conference", "Conference"),
        ("outreach", "Outreach"),
        ("wedding", "Wedding"),
        ("funeral", "Funeral"),
        ("other", "Other"),
    ]

    entity = models.ForeignKey(
        EntityModel, on_delete=models.CASCADE, related_name="church_events"
    )
    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default="service")
    date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    # Attendees (members who attended or are attending)
    attendees = models.ManyToManyField(
        "Member", blank=True, related_name="events_attended"
    )

    
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_events"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.date})"

    class Meta:
        ordering = ["date", "start_time"]

class MemberRole(models.Model):
    """
    Through table: tracks which roles a member holds.
    """
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='member_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_members')
    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE)
    date_assigned = models.DateField()
    date_removed = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['member__full_name', 'role__name']

    def __str__(self):
        return f"{self.member.full_name} – {self.role.display_name}"

class Guild(models.Model):
    entity = models.ForeignKey(
        EntityModel,
        on_delete=models.CASCADE,
        related_name='guilds'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Guild'
        verbose_name_plural = 'Guilds'

    def __str__(self):
        return self.name

from django.db import models
from django_ledger.models import EntityModel

class ChurchConfig(models.Model):
    """
    Church-specific configuration settings.
    """
    entity = models.OneToOneField(
        EntityModel,
        on_delete=models.CASCADE,
        related_name='church_config'
    )

    # Basic Church Info
    church_name = models.CharField(max_length=200, blank=True, help_text="Full name of the church")
    church_tagline = models.CharField(max_length=200, blank=True, help_text="Church motto or tagline")
    founded_date = models.DateField(null=True, blank=True)
    denomination = models.CharField(max_length=100, blank=True)

    # Contact Details
    address = models.TextField(blank=True, help_text="Physical address")
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    # Service Settings
    default_service_name = models.CharField(max_length=100, default="Sunday Service", help_text="Default service name")
    service_days = models.JSONField(default=list, blank=True, help_text="Days services are held (e.g., ['Sunday', 'Wednesday'])")

    # Financial Settings
    default_offering_ledger = models.CharField(max_length=20, default='4010', help_text="Default ledger code for offerings")
    default_dues_ledger = models.CharField(max_length=20, default='4011', help_text="Default ledger code for dues")
    default_tithe_ledger = models.CharField(max_length=20, default='4012', help_text="Default ledger code for tithes")
    default_dayborn_ledger = models.CharField(max_length=20, default='4013', help_text="Default ledger code for dayborn")
    default_guild_ledger = models.CharField(max_length=20, default='4014', help_text="Default ledger code for guild offerings")
    default_special_ledger = models.CharField(max_length=20, default='4015', help_text="Default ledger code for special offerings")

    # Settings
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Church Configuration'
        verbose_name_plural = 'Church Configurations'

    def __str__(self):
        return f"{self.entity.name} - Church Config"


class DuesTithes(models.Model):
    """
    Per-member giving record. Created by a posting handler
    when a church giving Trans is posted to the journal.
    """

    CATEGORY_CHOICES = [
        ("dues", "Dues"),
        ("tithe", "Tithe"),
        ("offering", "Offering"),
        ("harvest", "Harvest"),
        ("christmas", "Christmas"),
        ("easter", "Easter"),
        ("special", "Special Thank Offering"),
        ("other", "Other"),
    ]

    entity = models.ForeignKey(
        "django_ledger.EntityModel",
        on_delete=models.CASCADE,
        related_name="dues_tithes",
    )
    member = models.ForeignKey(
        "ChurchApp.Member", on_delete=models.CASCADE, related_name="dues_tithes"
    )
    trans = models.OneToOneField(
        "RecPayApp.Trans", on_delete=models.CASCADE, related_name="dues_tithe"
    )
    date = models.DateField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    details = models.CharField(max_length=250, blank=True, default="")
    receipt_no = models.CharField(max_length=50, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]
        indexes = [
            models.Index(fields=["member", "-date"]),
            models.Index(fields=["entity", "-date"]),
        ]

    def __str__(self):
        return f"{self.member.full_name} – {self.get_category_display()} ₵{self.amount}"


class MemberContribution(models.Model):
    """
    One row per member giving receipt.
    Created automatically for any POSTED church Receipts Trans
    that has a member. The ledger_name is stored as the category —
    new church schemes work without code changes.
    """

    entity = models.ForeignKey(
        "django_ledger.EntityModel",
        on_delete=models.CASCADE,
        related_name="member_contributions",
    )
    member = models.ForeignKey("ChurchApp.Member", on_delete=models.CASCADE, related_name="contributions")
    trans = models.OneToOneField("RecPayApp.Trans", on_delete=models.CASCADE, related_name="contribution")

    date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    ledger_code = models.CharField(max_length=20, blank=True, default="")
    ledger_name = models.CharField(
        max_length=100, blank=True, default=""
    )  # "Dues", "Welfare Fund", ...
    details = models.CharField(max_length=250, blank=True, default="")
    receipt_no = models.CharField(max_length=50, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]
        indexes = [
            models.Index(fields=["member", "-date"]),
            models.Index(fields=["entity", "-date"]),
            models.Index(fields=["entity", "ledger_code"]),
        ]

    def __str__(self):
        return f"{self.member.full_name} - {self.ledger_name} ₵{self.amount}"
