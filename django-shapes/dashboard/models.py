from pyexpat import model
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
import string
import random
from multiselectfield import MultiSelectField

# Create your models here.

# def unique_username():
#     strings = string.ascii_uppercase + string.ascii_lowercase
#     username = ''.join(random.choice(strings) for i in strings)[:6]
#     while User.objects.filter(username=username).exists():
#         username = ''.join(random.choice(strings) for i in strings)[:6]
#     return username


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not username:
            raise ValueError('The given username must be set')

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_staff", False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    DEPARTMENT_CHOICES = (
        ('AD', 'AD'),
        ('BT', 'BT'),
        ('OT', 'OT'),
        ('ST', 'ST'),
        ('PT', 'PT'),
        ('SE', 'SE'),
        ('FO', 'FO')
    )
    department = models.CharField(max_length=2, choices=DEPARTMENT_CHOICES)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=120)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True)
    created_on = models.DateField(auto_now=True)
    created_by = models.CharField(max_length=200)
    objects = UserManager()

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username


class ClientTable(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    )
    ASSESSMENT_CHOICES = (
        ('BT', 'BT'),
        ('OT', 'OT'),
        ('ST', 'ST')
    )
    THEROPY_CHOICES = (
        ("BT", "BT"),
        ("OT", "OT"),
        ("ST", "ST"),
        ("PT", "PT"),
        ("SE", "SE"),
    )
    DISCONTINIOUS_CHOICES = (
        ('True', 'True'),
        ('False', 'False')
    )
    
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    dob = models.DateField(auto_now=False)
    age = models.CharField(max_length=200)
    email = models.EmailField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=12, blank=True,
                             null=True, default='123456789')
    alternate_phone = models.CharField(
        max_length=12, blank=True, null=True, default='123456789')
    mother_tongue = models.CharField(max_length=200)
    father_name = models.CharField(max_length=200)
    mother_name = models.CharField(max_length=200)
    address = models.TextField()
    branch = models.CharField(max_length=200)
    created_on = models.DateField(auto_now=False)
    created_by = models.CharField(max_length=200)
    modified_on = models.DateTimeField(auto_now=False, blank=True, null=True)
    modified_by = models.CharField(max_length=200)
    discontinious = models.CharField(
        max_length=8, default='False')
    discontinious_on = models.DateField(auto_now=False)
    assessment = MultiSelectField(max_length=10,max_choices=10, choices=ASSESSMENT_CHOICES)
    slot_time_from = models.TimeField(auto_now=False)
    slot_time_to = models.TimeField(auto_now=False)
    theropy = MultiSelectField(max_length=100,max_choices=10,choices=THEROPY_CHOICES )
    chief_complaints = models.TextField()
    diagnosis = models.TextField()
    remarks = models.TextField()

    def __str__(self):
        return self.name


class Assesment(models.Model):
    GENDER = (
        ("M", "Male"),
        ("F", "Female"),
    )
    TEST_CHOICES = (
        ('DST', 'DST'),
        ('VSMS', 'VSMS'),
        ('MISIC', 'MISIC')
    )
    clienttable = models.ForeignKey(ClientTable, on_delete=models.CASCADE)
    therapist = models.CharField(max_length=100)
    date_of_assessment = models.DateField(auto_now_add=False)
    prenatal_history = models.TextField()
    family_history = models.TextField()
    development_history = models.TextField()
    school_history = models.TextField()
    tests_administered = models.CharField(max_length=6, choices=TEST_CHOICES)
    test_results = models.IntegerField()
    behavioural_observation = models.TextField()
    impression = models.TextField()
    recommendations = models.TextField()
    created_on = models.DateField(auto_now=True)
    created_by = models.CharField(max_length=200)
    modified_on = models.DateTimeField(auto_now=False, blank=True, null=True)
    modified_by = models.CharField(max_length=200)
    email_sent = models.CharField(max_length=10,default='')
    version = models.CharField(max_length=10)
    Status = models.CharField(max_length=50, default='Not Started')


class STAssesment(models.Model):
    clienttable = models.ForeignKey(ClientTable, on_delete=models.CASCADE)
    therapist = models.CharField(max_length=100)
    date_of_assessment = models.DateField(auto_now_add=False)
    babbling = models.TextField()
    first_word = models.TextField()
    main_mode_comm = models.TextField()
    family_history = models.TextField()
    motor_developments = models.TextField()
    oro_peripheral_mechanism = models.TextField()
    vegetative_skills = models.TextField()
    vision = models.TextField()
    hearing = models.TextField()
    response_to_name_call = models.TextField()
    environmental_sounds = models.TextField()
    eye_contact = models.TextField()
    attention_to_sound = models.TextField()
    imitation_to_body_movements = models.TextField()
    imitation_to_speech = models.TextField()
    attention_level = models.TextField()
    social_smile = models.TextField()
    initiates_interaction = models.TextField()
    receptive_language = models.TextField()
    expressive_language = models.TextField()
    provisional_diagnosis = models.TextField()
    recommendations = models.TextField()
    reels_RL_score = models.IntegerField()
    reels_EL_score = models.IntegerField()
    tests_administered = models.CharField(max_length=100, default='REELS')
    Status = models.CharField(max_length=50, default='Not Started')


class OTAssesment(models.Model):
    clienttable = models.ForeignKey(ClientTable, on_delete=models.CASCADE)
    therapist = models.CharField(max_length=100)
    date_of_assessment = models.DateField(auto_now_add=False)
    presenting_complaints = models.TextField()
    milestone_development = models.TextField()
    behavior_cognition = models.TextField()
    cognitive_skills = models.TextField()
    kinaesthesia = models.TextField()
    Status = models.CharField(max_length=50, default='Not Started')
