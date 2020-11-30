from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions, status
from rest_framework.authentication import BaseAuthentication
from django.db.models import Q
from daily import models, serializers
import time
import hashlib
import random
import requests
import json
import jieba.analyse
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

class MyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get("HTTP_AUTH")
        print(token)
        token = token[6:]
        token_obj = models.Token.objects.filter(token=token).first()
        if not token_obj:
            print(token_obj)
            raise exceptions.AuthenticationFailed('用户认证失败')
        return token_obj.user, token_obj

def make_token(user):
    current_time = str(time.time())
    hash_code = hashlib.md5(user.encode("utf-8"))
    hash_code.update(current_time.encode("utf-8"))
    return hash_code.hexdigest()

class Dream(APIView):
    authentication_classes = [MyAuthentication, ]

    @classmethod
    def get_analysis(cls, keywords):
        analysis_code = "002c048d89d74531a84110ee27880ce2"
        headers = {"Authorization": "APPCODE " + analysis_code}
        kw = {"keyword": keywords[0]}
        analysis_url = "https://jisudream.market.alicloudapi.com/dream/search"
        response = requests.get(analysis_url, params=kw, headers=headers)
        response_str = str(response.content, 'utf - 8')
        data = json.loads(response_str)
        print("使用阿里周公解梦接口获取到接口为", data)
        return data['result']
        pass

    @classmethod
    def get_keyword(cls, sentence):
        # tf-idf params
        topK = 2
        withWeight = False
        allowPOS = ()
        keywords_tfidf = jieba.analyse.extract_tags(sentence, topK, withWeight, allowPOS)
        if keywords_tfidf[0] == '梦到': keywords_tfidf[0] = keywords_tfidf[1]
        print('使用jieba获取到关键词为：', keywords_tfidf)
        return keywords_tfidf  # keyword list
        pass

    @classmethod
    def get_dream_by_date(cls, date_str):
        result = []
        for dream in models.Dream.objects.raw("select * from daily_dream where date(create_time) = '%s'" % (date_str,)):
            result.append(serializers.DreamModelSerializer(dream).data)
        return result

    @staticmethod
    def get(request):
        date_str = request.GET['date']
        dream = Dream.get_dream_by_date(date_str)
        print(dream)
        response = {'data': dream}
        return Response(response, status.HTTP_200_OK)

    @staticmethod
    def post(request):
        sentence = request.POST['content']
        keywords = Dream.get_keyword(sentence)
        analysis = Dream.get_analysis(keywords)

        dream_obj = models.Dream(
            user=request.user,
            content=sentence,
            keyword=keywords[0],
            analysis=json.dumps(analysis),
        )
        dream_obj.save()

        response = {"result": "success", "sentence": sentence, "analysis": analysis}
        return Response(response, status.HTTP_200_OK)

class GetSms(APIView):
    @staticmethod
    def post(request):
        print(request.POST)
        phone = request.POST['phone']
        user_obj = models.User.objects.filter(phone_number=phone).first()

        verify_code = random.randint(100000, 999999)
        models.Verify.objects.update_or_create(account=phone, type='ph', defaults={"code": str(verify_code)})
        client = AcsClient('', '', '')

        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https')  # https | http
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')

        request.add_query_param('RegionId', "cn-hangzhou")
        request.add_query_param('PhoneNumbers', phone)
        request.add_query_param('SignName', "光阴")
        request.add_query_param('TemplateCode', "SMS_189830981")
        request.add_query_param('TemplateParam', '{"code":"' + str(verify_code) + '"}')

        response = client.do_action_with_exception(request)
        print("验证码结果" + str(response, encoding='utf-8'))
        return Response({'result': 'success'}, status=status.HTTP_200_OK)

class AuthView(APIView):
    @staticmethod
    def post(request):
        print('登录', request.POST)
        nick_name = request.POST['nick_name'] if 'nick_name' in request.POST else False
        phone = request.POST['phone'] if 'phone' in request.POST else False
        password = request.POST['password'] if 'password' in request.POST else False
        verify = request.POST['verify'] if 'verify' in request.POST else False

        if verify:
            # 用验证码登录
            print('用验证码登录', phone)
            verify_obj = models.Verify.objects.filter(account=phone, code=verify)
            if verify_obj:
                user_obj = models.User.objects.filter(phone_number=phone).first()
                if not user_obj:
                    user_obj = models.User(phone_number=phone)
                    user_obj.save()
                    user_obj = models.User.objects.filter(phone_number=phone).first()
                token = make_token(phone)
                models.Token.objects.update_or_create(user=user_obj, defaults={"token": token})
                response = {
                    "token": token,
                    "phone_number": phone,
                    "nickname": user_obj.nick_name
                }
                print(token, phone)
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response({'result': 'failure'}, status=status.HTTP_200_OK)

        else:
            # 用户名+密码登录
            user_obj = models.User.objects.filter(nick_name=nick_name,password=password).first()
            if user_obj:
                token = make_token(nick_name)
                models.Token.objects.update_or_create(user=user_obj, defaults={"token": token})
                response = {
                    "token": token,
                    "nickname": nick_name
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response({'result': 'failure'}, status=status.HTTP_200_OK)

class Account(APIView):
    authentication_classes = [MyAuthentication, ]

    @staticmethod
    def post(request):
        name = request.POST['name'] if 'name' in request.POST else False
        pw = request.POST['pw'] if 'pw' in request.POST else False
        if name and pw:
            user_obj = request.user
            user_obj.nick_name = name
            user_obj.password = pw
            user_obj.save()
            return Response({'result': 'success'}, status=status.HTTP_200_OK)
        else:
            return Response({'result': 'wrong params'}, status=status.HTTP_200_OK)

class Friend(APIView):
    authentication_classes = [MyAuthentication, ]

    @staticmethod
    def post(request):
        nick_name = request.POST['nick_name'] if 'nick_name' in request.POST else False
        if nick_name:
            user_obj = models.User.objects.filter(nick_name=nick_name).first()
            if user_obj:
                sender_obj = models.Friend.objects.filter(sender=request.user, receiver=user_obj).first()
                receiver_obj = models.Friend.objects.filter(receiver=request.user, sender=user_obj).first()
                if sender_obj:
                    sender_obj.sender_attitude = True
                    sender_obj.save()
                    return Response({'result': 'add success'}, status=status.HTTP_200_OK)
                elif receiver_obj:
                    receiver_obj.receiver_attitude = True
                    receiver_obj.save()
                    return Response({'result': 'add success'}, status=status.HTTP_200_OK)
                else:
                    if user_obj.id is not request.user.id:
                        friend_obj = models.Friend(
                            sender=request.user,
                            receiver = user_obj,
                            sender_attitude = True,
                            receiver_attitude = False,
                        )
                        friend_obj.save()
                        return Response({'result': 'add success'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'result': 'is self'}, status=status.HTTP_200_OK)
            else:
                return Response({'result': 'wrong nick_name'}, status=status.HTTP_200_OK)
        else:
            return Response({'result': 'wrong params'}, status=status.HTTP_200_OK)

    @staticmethod
    def get(request):
        friend_receiver_qs = models.Friend.objects.filter(Q(receiver=request.user) & Q(sender_attitude=True) & Q(receiver_attitude=True)).all()
        friend_sender_qs = models.Friend.objects.filter(Q(sender=request.user) & Q(sender_attitude=True) & Q(receiver_attitude=True)).all()
        friend_receiver = serializers.FriendReceiverModelSerializer(instance=friend_receiver_qs, many=True)
        friend_sender = serializers.FriendSenderModelSerializer(instance=friend_sender_qs, many=True)
        response = {"data": friend_receiver.data + friend_sender.data}
        return Response(response, status=status.HTTP_200_OK)
        pass

class Sparklers(APIView):
    authentication_classes = [MyAuthentication, ]

    @staticmethod
    def post(request):
        receiver_id = request.POST['receiver_id'] if 'receiver_id' in request.POST else False
        message = request.POST['message'] if 'message' in request.POST else False
        if receiver_id and message:
            receiver_obj = models.User.objects.get(id=receiver_id)
            sparklers_obj = models.Sparklers(
                sender=request.user,
                receiver=receiver_obj,
                isRead=False,
                message=message,
            )
            sparklers_obj.save()
            return Response({'result': 'success'}, status=status.HTTP_200_OK)
        else:
            return Response({'result': 'wrong params'}, status=status.HTTP_200_OK)

    @staticmethod
    def get(request):
        sparklers_id = request.GET['sparklers_id'] if 'sparklers_id' in request.GET else False
        receiver_id = request.GET['receiver_id'] if 'receiver_id' in request.GET else False
        if sparklers_id:
            sparklers_obj = models.Sparklers.objects.get(id=int(sparklers_id))
            sparklers_obj.isRead = True
            sparklers_obj.save()
            return Response({'result': 'success'}, status=status.HTTP_200_OK)
        else:
            data = []
            receiver_obj = models.User.objects.get(id=receiver_id)
            sparklers_qs = models.Sparklers.objects.filter((Q(sender=request.user) & Q(receiver=receiver_obj) & Q(isRead=False)) | (Q(sender=receiver_obj) & Q(receiver=request.user) & Q(isRead=False))).order_by('create_time')
            for sparkler in sparklers_qs:
                data.append({
                    'message': sparkler.message,
                    'id': sparkler.id,
                    'is_self': True if sparkler.sender == request.user else False
                })
            return Response({'data': data}, status=status.HTTP_200_OK)

class Stranger(APIView):
    authentication_classes = [MyAuthentication, ]

    @staticmethod
    def get(request):
        friend_qs = models.Friend.objects.filter(receiver=request.user, receiver_attitude=False)
        friend_obj = serializers.FriendReceiverModelSerializer(instance=friend_qs, many=True)
        response = {"data": friend_obj.data}
        return Response(response, status=status.HTTP_200_OK)

class TreeHole(APIView):
    authentication_classes = [MyAuthentication, ]

    @staticmethod
    def post(request):
        pass

    @staticmethod
    def get(request):
        pass
