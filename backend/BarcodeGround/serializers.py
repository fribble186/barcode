from rest_framework.serializers import ModelSerializer, SerializerMethodField
from BarcodeGround import models
import json

class UserModelSerializer(ModelSerializer):
    class Meta:
        model = models.User
        fields = '__all__'

class ProductModelSimpleSerializer(ModelSerializer):
    class Meta:
        model = models.Product
        fields = '__all__'

class ProductModelDetailSerializer(ModelSerializer):
    comment = SerializerMethodField(source='get_comment')
    class Meta:
        model = models.Product
        fields = ('id', 'image_url', 'name', 'origin', 'price', 'comment')

    @staticmethod
    def get_comment(obj):
        return CommentModelSerializer(obj.comment_product, many=True).data

class CommentModelSerializer(ModelSerializer):
    user = SerializerMethodField(source='get_user')
    star = SerializerMethodField(source='get_star')
    unstar = SerializerMethodField(source='get_unstar')
    class Meta:
        model = models.Comment
        fields = ('user', 'comment', 'star', 'unstar')

    @staticmethod
    def get_user(obj):
        return UserModelSerializer(obj.user, many=False).data

    @staticmethod
    def get_star(obj):
        return list(range(1, obj.ranking+1))

    @staticmethod
    def get_unstar(obj):
        return list(range(1, 6-obj.ranking))