from django.db import models
from django_mysql.models import JSONField

class User(models.Model):
    """
    用户表
    """
    nick_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="用户昵称"
    )
    avatar_url = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="用户头像url"
    )
    gender = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="用户性别"
    )
    user_type = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="自定义用户类型"
    )
    phone_number = models.CharField(
        max_length=12,
        null=True,
        blank=True,
        verbose_name="用户手机号"
    )
    email = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="用户电子邮箱"
    )
    password = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="用户密码"
    )
    def __str__(self):
        return self.openid

class Token(models.Model):
    """
    用户登录凭证token
    """
    user = models.OneToOneField(
        User,
        related_name='user_token',
        on_delete=models.CASCADE
    )
    token = models.CharField(
        max_length=64
    )
    session_key = models.CharField(
        max_length=100
    )
    create_time = models.DateTimeField(
        auto_now_add=True
    )
    update_time = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.token

class Verify(models.Model):
    """
    验证码表
    """
    type = models.CharField(
        max_length=2,
        verbose_name="验证类型"
    )
    account = models.CharField(
        max_length=50,
        verbose_name="验证账户信息"
    )
    code = models.CharField(
        max_length=10,
        verbose_name="验证码"
    )

class Dream(models.Model):
    """
    梦记录表
    """
    user = models.ForeignKey(
        User,
        related_name='dream_user',
        on_delete=models.CASCADE
    )
    content = models.TextField(
        null=True,
        blank=True
    )
    analysis = JSONField()
    keyword = models.CharField(
        null=True,
        blank=True,
        max_length=10
    )
    tag = models.CharField(
        null=True,
        blank=True,
        max_length=10
    )
    ranking = models.IntegerField(
        null=True,
        blank=True
    )
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

class Friend(models.Model):
    """
    用户好友关系表
    """
    sender = models.ForeignKey(
        User,
        related_name='friend_sender',
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User,
        related_name='friend_receiver',
        on_delete=models.CASCADE
    )
    sender_attitude = models.BooleanField(
        null=True,
        blank=True
    )
    receiver_attitude = models.BooleanField(
        null=True,
        blank=True
    )
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

class Sparklers(models.Model):
    """
    聊天表
    """
    sender = models.ForeignKey(
        User,
        related_name='sparklers_sender',
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User,
        related_name='sparklers_receiver',
        on_delete=models.CASCADE
    )
    message = models.CharField(
        null=True,
        blank=True,
        max_length=150
    )
    isRead = models.BooleanField(
        null=True,
        blank=True
    )
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

class TreeHole(models.Model):
    """
    树洞记录表
    """
    sender = models.ForeignKey(
        User,
        related_name='tree_hole_sender',
        on_delete=models.CASCADE
    )
    message = models.CharField(
        null=True,
        blank=True,
        max_length=150
    )
    favor_count = models.IntegerField(
        null=True,
        blank=True,
        default=0
    )
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
