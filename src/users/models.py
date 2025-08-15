from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.postgres.fields import ArrayField
from classe.models import Classe
from filiere.models import Filiere
from module.models import Module
from role.models import Role
from django.utils import timezone



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse e-mail est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Le superutilisateur doit avoir is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Le superutilisateur doit avoir is_superuser=True.")

        return self.create_user(email, password, **extra_fields)



# Le Model Utilisateur
class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True, blank=False)
    password = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=8, blank=True)

    fonction = models.CharField(max_length=150, blank=True)  #pour les personnels

    #Relation
    #Pour les etudiants
    classe = models.ForeignKey(Classe, on_delete=models.SET_NULL, null=True, related_name="users")
    filiere = models.ForeignKey(Filiere, on_delete=models.SET_NULL, null=True, related_name="users")

    #Pour les professeur
    modules = models.ManyToManyField(Module, related_name="users", blank=True)
    # Relation entre la table User et Role
    roles = models.ManyToManyField(Role, related_name="users" )

    # Dans votre modèle User backend
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    @classmethod
    def get_students(cls):
        return cls.objects.filter(roles__name='STUDENT').distinct()

    @classmethod
    def get_professors(cls):
        return cls.objects.filter(roles__name='PROFESSOR').distinct()

    @classmethod
    def get_admins(cls):
        return cls.objects.filter(is_staff=True)

    @classmethod
    def get_regular_admins(cls):
        return cls.objects.filter(is_staff=True, is_superuser=False)

    @classmethod
    def get_noadmins(cls):
        return cls.objects.filter(is_staff=False)











    def __str__(self):
        return self.email