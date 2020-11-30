from django.db import models

class User(models.Model):
    """
    用户表
    """
    nick_name = models.CharField(
        max_length=50,
        verbose_name="用户昵称"
    )
    openid = models.CharField(
        max_length=50,
        verbose_name="用户微信id"
    )
    avatar_url = models.CharField(
        max_length=200,
        verbose_name="用户头像url"
    )
    gender = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="用户性别"
    )
    country = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name="用户所在国家"
    )
    province = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name="用户所在省份"
    )
    city = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name="用户所在城市"
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

class Product(models.Model):
    """
    商品表
    """
    barcode = models.CharField(
        max_length=30,
        verbose_name="商品条码"
    )
    name = models.CharField(
        max_length=30,
        verbose_name="商品名称"
    )
    ins_name = models.CharField(
        max_length=50,
        verbose_name="生产公司名称",
        null=True,
        blank=True
    )
    ins_address = models.CharField(
        max_length=100,
        verbose_name="生产公司地址",
        null=True,
        blank=True
    )
    spec = models.CharField(
        max_length=30,
        verbose_name="商品规格",
        null=True,
        blank=True
    )
    price = models.CharField(
        max_length=20,
        verbose_name="商品价格",
        null=True,
        blank=True
    )
    image_url = models.CharField(
        max_length=100,
        verbose_name="商品图片url",
        null=True,
        blank=True
    )
    goods_type = models.CharField(
        max_length=50,
        verbose_name="商品类型",
        null=True,
        blank=True
    )
    origin = models.CharField(
        max_length=50,
        verbose_name="商品原产地",
        null=True,
        blank=True
    )
    brand = models.CharField(
        max_length=50,
        verbose_name="商品品牌",
        null=True,
        blank=True
    )
    remark = models.CharField(
        max_length=300,
        verbose_name="商品其他信息",
        null=True,
        blank=True
    )
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.barcode + self.name

class Comment(models.Model):
    """
    评论表
    """
    user = models.ForeignKey(
        User,
        related_name='comment_user',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        related_name='comment_product',
        on_delete=models.CASCADE
    )
    comment = models.CharField(
        max_length=200
    )
    ranking = models.IntegerField(
        null=True,
        blank=True
    )
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
