from rest_framework.serializers import ModelSerializer, SerializerMethodField
from daily import models
import json

class DreamModelSerializer(ModelSerializer):
    class Meta:
        model = models.Dream
        fields = '__all__'

class UserModelSerializer(ModelSerializer):
    class Meta:
        model = models.User
        fields = '__all__'

class FriendReceiverModelSerializer(ModelSerializer):
    user_detail = SerializerMethodField(source='get_user_detail')
    class Meta:
        model = models.Friend
        fields = ('user_detail', )

    @staticmethod
    def get_user_detail(obj):
        return UserModelSerializer(obj.sender, many=False).data

class FriendSenderModelSerializer(ModelSerializer):
    user_detail = SerializerMethodField(source='get_user_detail')
    class Meta:
        model = models.Friend
        fields = ('user_detail', )

    @staticmethod
    def get_user_detail(obj):
        return UserModelSerializer(obj.receiver, many=False).data

class SparklersSelfModelSerializer(ModelSerializer):
    is_self = SerializerMethodField(source='get_is_self')
    class Meta:
        model = models.Sparklers
        fields = ('id', 'message', 'is_self')

    @staticmethod
    def get_is_self(obj):
        return True

class SparklersFriendModelSerializer(ModelSerializer):
    is_self = SerializerMethodField(source='get_is_self')

    class Meta:
        model = models.Sparklers
        fields = ('id', 'message', 'is_self')

    @staticmethod
    def get_is_self(obj):
        return False
