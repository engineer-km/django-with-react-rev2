from pydoc import resolve
from turtle import title
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.shortcuts import resolve_url
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.db import models


class User(AbstractUser):
    class GenderChoices(models.TextChoices):
        # DB저장값, 보여지는 값
        MALE = "M", "남성"
        FEMAIL = "F", "여성"

    # User 간의 관계
    follower_set = models.ManyToManyField("self", blank=True, symmetrical=False)  # 유저`를` 팔로우한 사람
    following_set = models.ManyToManyField("self", blank=True) # 유저`가` 팔로잉 하는 사람

    website_url = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=13, blank=True, 
                                    validators=[RegexValidator(r"^010-?[1-9]\d{3}-?\d{4}$")])
    gender = models.CharField(max_length=1, blank=True,
                              choices=GenderChoices.choices)
    avatar = models.ImageField(blank=True, 
                               upload_to="accounts/avatar/%Y%m%d",
                               help_text="48px * 48px 크기의 png/jpg 파일을 업로드 해주세요.")

    @property
    def name(self):
        return "{} {}".format(self.first_name, self.last_name)
    
    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        else:
            return resolve_url('pydenticon_image', self.username)

    def send_welcome_email(self):
        subject = render_to_string(
            "accounts/welcome_email_subject.txt", 
            { "user": self, }
        )
        content = render_to_string(
            "accounts/welcome_email_content.txt",
            { "user": self, }
        )
        sender_email = settings.EMAIL_HOST_USER
        # google 계정이 2단계인증으로 되어있을 경우
        # google https://support.google.com/mail/?p=InvalidSecondFactor 앱 전용 비번 생성후, 
        # 해당 16글자의 비번을 .env 에 적기
        '''
        send_mail(subject, content, sender_email, 
                  [self.email], fail_silently=False)
        '''
        
        


#class Profile(models.Model):
#    pass