import re
from django.db import models
from django.core import validators
from django.utils import timezone
from django.core.mail import send_mail
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator
from django.conf import settings
import datetime
import time

class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        now = timezone.now()
        if not email:
            raise ValueError(_('The given email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, is_staff=is_staff, is_active=True, is_superuser=is_superuser, last_login=now, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)
    def create_superuser(self, email, password, **extra_fields):
        user=self._create_user(email, password, True, True, **extra_fields)
        user.is_active=True
        user.save(using=self._db)
        return user

class Client(models.Model):
    name = models.CharField(max_length=300)
    # CNPJ = models.CharField(max_length=16, unique=True)
    def __str__(self):
        return self.name

# class Workplace(models.Model):
#     owner = models.ForeignKey(Client, on_delete=models.CASCADE)
#     latitude = models.FloatField(null=True, blank=True)
#     longitude = models.FloatField(null=True, blank=True)
#     latitudeDelta = models.FloatField(null=True, blank=True)
#     longitudeDelta = models.FloatField(null=True, blank=True)

    # def __str__(self):
    #     return self.user_id

class Location(models.Model):

    owner = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    latitudeDelta = models.FloatField()
    longitudeDelta = models.FloatField()

    def __str__(self):
        return self.name

    # REQUIRED_FIELDS = ['latitude', 'longitude', 'latitudeDelta', 'longitudeDelta']

class User(AbstractBaseUser, PermissionsMixin):

    def upload_path(self, filename):
        millis = str(round(time.time() * 1000))
        return "profile_pics/"+str(self.pk)+'/'+millis+filename

    def upload_document_path(self, filename):
        print(filename)
        print(self.pk)
        return "documents/"+str(self.pk)+'/'+filename

    # username = models.CharField(_('username'), max_length=15, unique=True, help_text=_('Required. 15 characters or fewer. Letters, numbers and @/./+/-/_ characters'), validators=[ validators.RegexValidator(re.compile('^[\w.@+-]+$'), _('Enter a valid username.'), _('invalid'))])
    # first_name = models.CharField(_('first name'), max_length=30)
    # last_name = models.CharField(_('last name'), max_length=30)
    full_name = models.CharField(_('full name'), max_length=300)
    email = models.EmailField(_('email address'), max_length=255, unique=True)
    profile_pic = models.ImageField(upload_to=upload_path, blank=True)
    CPF = models.CharField(_('CPF'),max_length=16, unique=True)
    cellphone = models.CharField(_('cellphone'),max_length=30, null=True, blank=True)
    birthdate = models.DateTimeField(_('birthdate'),null=True, blank=True)
    usertype = models.IntegerField(_('usertype'), validators=[MaxValueValidator(5)], null=True, blank=True)
    sign_in_status = models.IntegerField(_('sign in status'), validators=[MaxValueValidator(7)], null=True, blank=True)
    sign_in_date = models.DateTimeField(null=True, blank= True)
    sign_review_date = models.DateTimeField(null=True, blank= True)
    sign_validation_date = models.DateTimeField(null=True, blank= True)
    user_code = models.IntegerField(_('user code'),  validators=[MaxValueValidator(999999999)], null=True, blank=True)
    channel_name = models.CharField(_('channel name'), max_length=300, null=True, blank=True)
    workplace = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    user_who_requested = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    busy = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    latitudeDelta = models.FloatField(null=True, blank=True)
    longitudeDelta = models.FloatField(null=True, blank=True)
    access_token = models.TextField(_('access token'), null=True, blank=True)
    access_token_created_at = models.DateTimeField(_('access token created at'),null=True, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False, help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True, help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'))
    
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    is_trusty = models.BooleanField(_('trusty'), default=False, help_text=_('Designates whether this user has confirmed his account.'))
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'CPF']

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    def get_full_name(self):
        # full_name = '%s %s' % (self.first_name, self.last_name)
        full_name = self.full_name
        # return full_name.strip()
        return full_name
    def get_short_name(self):
        short_name = self.full_name.split(' ')[0]
        return short_name
    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])


class OfficialDocumentPic(models.Model):

    def upload_document_path(self, filename):
        print(filename)
        print(User.objects.get(email=self.user_id).pk)
        return "documents/"+str(User.objects.get(email=self.user_id).pk)+'/'+filename
    
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=100)
    document_pic = models.ImageField(upload_to=upload_document_path, blank=True)

    def __str__(self):
        return str(User.objects.get(email=self.user_id))

class SituationalDocumentPic(models.Model):

    def upload_document_path(self, filename):
        print(filename)
        print(User.objects.get(email=self.user_id).pk)
        return "documents/"+str(User.objects.get(email=self.user_id).pk)+'/'+filename
    
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=100)
    document_pic = models.ImageField(upload_to=upload_document_path, blank=True)

    def __str__(self):
        return str(User.objects.get(email=self.user_id))

class FAQCategory(models.Model):

    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class FAQ(models.Model):

    question = models.TextField()
    aunswer = models.TextField()
    category = models.ForeignKey(FAQCategory, on_delete=models.CASCADE, null=True, blank=True)

    REQUIRED_FIELDS = ['question', 'category']

    def __str__(self):
        return self.question

class Teste(models.Model):
    stringArr = ArrayField(models.ImageField(upload_to='upload_path', blank=True),size=8)