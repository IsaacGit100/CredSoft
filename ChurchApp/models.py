from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
# ChurchApp/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import choices
from django_ledger.models import (
    EntityModel,
    JournalEntryModel,
    TransactionModel,
    AccountModel,
)

# ---------- Parent/Guardian ----------


class Member(models.Model):

    ROLE_CHOICES = [
        ("Accounts", "Accounts"),
        ("Parish-Clerk", "Parish-Clerk"),
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
    first_name = models.CharField(max_length=100)
    other_names = models.CharField(max_length=100, blank=True, default="")
    last_name = models.CharField(max_length=100, blank=True, default="")
    full_name = models.CharField(max_length=200, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    telephone1 = models.CharField(max_length=20, blank=True, default="")
    telephone2 = models.CharField(max_length=20, blank=True, default="")
    postal_address = models.CharField(max_length=150, blank=True, default="")
    res_address = models.CharField(max_length=150, blank=True, default="")
    near_landmark = models.CharField(max_length=100, null=True, blank=True, default="")
    education_level = models.CharField(max_length=50, null=True, blank=True, choices=EDUCATION_CHOICES, default="")
    profession = models.CharField(max_length=100, blank=True, default="")
    ghana_card_no = models.CharField(max_length=15, null=True, default="", blank=True)

    date_of_birth = models.DateField(default=None, null=True, blank=True)
    date_baptised = models.DateField(default=None, null=True, blank=True)
    date_confirmed = models.DateField(default=None, null=True, blank=True)
    date_enrolled = models.DateField(default=None, null=True, blank=True)
    date_expired = models.DateField(default=None, null=True, blank=True)

    guild_first = models.CharField(max_length=120, blank=True, default="")   # select from guilds model
    guild_second = models.CharField(max_length=120, blank=True, default="")  # select from guilds model
    guild_third = models.CharField(max_length=120,  blank=True, default="")  # select from guilds model

    no_of_children = models.IntegerField(default=0, null=True, blank=True)
    names_of_children = models.JSONField()
    # Office information
    office_name = models.CharField(max_length=150, blank=True, default="")
    office_address = models.CharField(max_length=100, blank=True, default="")
    office_res_address = models.CharField(max_length=120, blank=True, default="")
    office_phone = models.CharField(max_length=150, blank=True, default="")
    office_email = models.EmailField(blank=True, default="")
    nature_of_business = models.CharField(max_length=150, blank=True, default="")

    # Spouse information (corrected duplicate fields)
    spouse_title = models.CharField(max_length=20, choices=TITLE_CHOICES, blank=True, null=True)
    spouse_name = models.CharField(max_length=100, blank=True, default="")
    spouse_postal_address = models.CharField(max_length=100, blank=True, default="")
    spouse_email_address = models.EmailField(blank=True, default="")
    spouse_telephone = models.CharField(max_length=20, blank=True, default="") 
    spouse_company_name = models.CharField(max_length=150, blank=True, default="")
    spouse_res_address = models.CharField(max_length=150, blank=True, default="")
    spouse_religion = models.CharField(
        max_length=150, choices=RELIGION_CHOICES, blank=True, default=""
    )
    spouse_occupation = models.CharField(max_length=100, blank=True, default="")
    spouse_education_level = models.CharField(
        max_length=120, choices=EDUCATION_CHOICES, blank=True, default=""
    )
    spouse_date_of_birth = models.DateField(default=None, null=True, blank=True)
    spouse_near_landmark = models.CharField(
        max_length=100, null=True, blank=True, default=""
    )
    spouse_religion = models.CharField(
        max_length=100, null=True, blank=True, default=""
    )
    spouse_church = models.CharField(max_length=100, null=True, blank=True, default="")

    father_name = models.CharField(max_length=100, null=True, blank=True, default="")
    father_res_address = models.CharField(max_length=100, null=True, blank=True, default="")
    father_telephone = models.CharField(max_length=15, null=True, blank=True, default="")
    father_deceased = models.BooleanField()

    mother_name = models.CharField(max_length=100, null=True, blank=True, default="")
    mother_res_address = models.CharField(max_length=100, null=True, blank=True, default="")
    mother_telephone = models.CharField(max_length=15, null=True, blank=True, default="")
    mother_deceased = models.BooleanField()
    is_deleted = models.BooleanField(default=False, help_text="Soft delete flag")

    # Optional: link to shared entity
    # entity = models.ForeignKey('core.Entity', on_delete=models.CASCADE, default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name="clergy")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="clergy_member")
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


class Staff(models.Model):
    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name="staff")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="staff_member")
    title = models.CharField(max_length=50, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, default="")
    other_names = models.CharField(max_length=50, blank=True, default="")
    last_name = models.CharField(max_length=100, blank=True, default="")
    full_name = models.CharField(max_length=200, blank=True)
    email_address = models.EmailField(null=True, blank=True, default='')
    telephone = models.CharField(max_length=20, null=True, blank=True, default='')
    postal_address = models.CharField(max_length=150, blank=True, default="")
    res_address = models.CharField(max_length=150, blank=True, default="")
    date_arrived = models.DateField(null=True, blank=True, default=None)
    date_depart = models.DateField(null=True, blank=True, default=None)
    role = models.CharField(max_length=20, null=True, blank=True)

    def save(self, *args, **kwargs):
        name_parts = filter(None, [self.first_name, self.other_names, self.last_name])
        self.full_name = " ".join(name_parts).strip()
        super().save(*args, **kwargs)


class Guilds(models.Model):
    Name = models.CharField(max_length=20, null=True, blank=True, default='')
    Description = models.CharField(max_length=50, null=True, blank=True, default='')


from django.db import models
from django_ledger.models import EntityModel
from django.contrib.auth.models import User


class Ushers(models.Model):
    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name="ushers")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="usher_member")
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class Guild(models.Model):
    entity = models.ForeignKey(
        EntityModel, on_delete=models.CASCADE, related_name="guilds"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Officiant(models.Model):
    
    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name="officiants")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="Off_member"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    entity = models.ForeignKey(
        EntityModel, on_delete=models.CASCADE, related_name="services"
    )
    date = models.DateField()
    name_of_service = models.CharField(max_length=100)
    officiant = models.ForeignKey(
        Officiant, on_delete=models.SET_NULL, null=True, blank=True
    )

    # JSON fields for lists
    clergy = models.JSONField(default=list, blank=True)  # List of clergy names/ids
    ushers = models.JSONField(default=list, blank=True)  # List of usher names/ids

    attendance = models.PositiveIntegerField(default=0)
    communicants = models.PositiveIntegerField(default=0)

    # Offerings (Decimal fields)
    general_offertory = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.00
    )

    # DayBorn offerings – store as JSON with day names and amounts
    day_born_offerings = models.JSONField(
        default=dict, blank=True
    )  # {"Monday": 10.00, "Tuesday": 5.00, ...}

    # Guild offerings – JSON list of {guild_name, amount}
    guild_offerings = models.JSONField(default=list, blank=True)

    dues = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    tithes = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    # Special/seasonal offerings – JSON lists of {description, amount}
    special_thank_offering = models.JSONField(default=list, blank=True)
    easter_offering = models.JSONField(default=list, blank=True)
    christmas_offering = models.JSONField(default=list, blank=True)
    harvest_offering = models.JSONField(default=list, blank=True)
    other_collections = models.JSONField(default=list, blank=True)

    # Computed field (can be calculated in save)
    grand_total = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    # Audit
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(default=None)
    updated_at = models.DateTimeField(default=None)

    # Link to journal entry
    journal_entry_id = models.CharField(max_length=50, null=True, blank=True)
    posted_to_ledger = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.date} – {self.name_of_service}"

    def save(self, *args, **kwargs):
        # Calculate grand_total from all offering fields
        total = self.general_offertory or 0
        total += (
            sum(self.day_born_offerings.values())
            if isinstance(self.day_born_offerings, dict)
            else 0
        )
        total += sum(
            item.get("amount", 0)
            for item in self.guild_offerings
            if isinstance(item, dict)
        )
        total += self.dues or 0
        total += self.tithes or 0
        total += sum(
            item.get("amount", 0)
            for item in self.special_thank_offering
            if isinstance(item, dict)
        )
        total += sum(
            item.get("amount", 0)
            for item in self.easter_offering
            if isinstance(item, dict)
        )
        total += sum(
            item.get("amount", 0)
            for item in self.christmas_offering
            if isinstance(item, dict)
        )
        total += sum(
            item.get("amount", 0)
            for item in self.harvest_offering
            if isinstance(item, dict)
        )
        total += sum(
            item.get("amount", 0)
            for item in self.other_collections
            if isinstance(item, dict)
        )
        self.grand_total = total
        super().save(*args, **kwargs)

# ChurchApp/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django_ledger.models import EntityModel

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

    # Audit fields
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_events"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.date})"

    class Meta:
        ordering = ["date", "start_time"]
