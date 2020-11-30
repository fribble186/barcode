from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions, status
from BarcodeGround import models, serializers, WXBizDataCrypt
from snownlp import SnowNLP
import requests
import json
import time
import hashlib


class MyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")
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

def login(user_id):
    user_obj = models.User.objects.filter(openid=user_id).first()
    return user_obj

def register(app_id, session_key, encrypted_data, iv):
    pc = WXBizDataCrypt.WXBizDataCrypt(app_id, session_key)
    user_info = pc.decrypt(encrypted_data, iv)
    print(user_info)
    user_obj = models.User(nick_name='未知' if user_info['nickName'] == '' else user_info['nickName'],
                           openid=user_info['openId'],
                           avatar_url='未知' if user_info['avatarUrl'] == '' else user_info['avatarUrl'],
                           gender='未知' if user_info['gender'] == '' else user_info['gender'],
                           country='未知' if user_info['country'] == '' else user_info['country'],
                           province='未知' if user_info['province'] == '' else user_info['province'],
                           city='未知' if user_info['city'] == '' else user_info['city'],
                           )
    user_obj.save()
    user_obj = models.User.objects.filter(openid=user_info['openId']).first()
    return user_obj


class AuthView(APIView):
    @staticmethod
    def post(request):
        # 获取数据
        app_id = "wx81bfda6b1ee9456c"
        secret = ""
        auth_code = request.POST['auth_code']
        encrypted_data = request.POST['encryptedData']
        iv = request.POST['iv']

        # 通过code2session接口获取code
        code2session_url = "https://api.weixin.qq.com/sns/jscode2session?appid=" + app_id + "&secret=" + secret +"&js_code="+ auth_code + "&grant_type=authorization_code"
        code2session_request = requests.get(code2session_url)
        session_key = code2session_request.json()['session_key']
        openid = code2session_request.json()['openid']

        # 登录或注册逻辑
        user_obj = login(openid)
        if not user_obj:
            user_obj = register(app_id, session_key, encrypted_data, iv)
        if user_obj:
            token = make_token(openid)
            models.Token.objects.update_or_create(user=user_obj, defaults={"token": token})
            response = {
                "token": token,
                "openId": openid
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

class BarcodeInfo(APIView):
    @staticmethod
    def get_product_from_api(code):
        barcode_app_code = "002c048d89d74531a84110ee27880ce2"
        headers = {"Authorization": "APPCODE " + barcode_app_code}
        kw = {"code": code}
        response = requests.get("http://codequery.market.alicloudapi.com/querybarcode", params=kw, headers=headers)
        response_str = str(response.content, 'utf - 8')
        data = json.loads(response_str)
        print(data)
        if data['msg']=='暂无数据！':
            return {'NO_DATA': True}
        result = data['result']
        product_obj = models.Product(
            barcode = code,
            name = result['goodsName'],
            ins_name = result['manuName'],
            ins_address = result['manuAddress'],
            spec = result['spec'],
            price = result['price'],
            image_url = result['img'],
            goods_type = result['goodsType'],
            origin = result['ycg'],
            brand = result['trademark'],
            remark = result['remark']
        )
        product_obj.save()
        product_obj = models.Product.objects.filter(barcode=code).first()
        return product_obj

    @staticmethod
    def get_product_from_database(code):
        product_obj = models.Product.objects.filter(barcode=code).first()
        return product_obj

    @staticmethod
    def get(request):
        if request.GET.get('code'):
            code = request.GET.get('code')
            product_obj = BarcodeInfo.get_product_from_database(code)
            if not product_obj:
                product_obj = BarcodeInfo.get_product_from_api(code)
            if product_obj:
                if isinstance(product_obj,dict):
                    return Response({'NO_DATA': True}, status.HTTP_200_OK)
                else:
                    product = serializers.ProductModelDetailSerializer(product_obj)
                    response = {"data": product.data}
            return Response(response, status.HTTP_200_OK)

        else:
            return Response({}, status.HTTP_200_OK)

class Comment(APIView):
    authentication_classes = [MyAuthentication, ]

    @staticmethod
    def rank_sentiments(sentiments):
        if sentiments >= 0.8:
            return 5
        elif sentiments >= 0.6:
            return 4
        elif sentiments >= 0.4:
            return 3
        elif sentiments >= 0.2:
            return 2
        else:
            return 1

    @staticmethod
    def sentiment_analysis(text):
        snownlp = SnowNLP(text)
        return Comment.rank_sentiments(snownlp.sentiments)

    @staticmethod
    def post(request):
        comment = request.POST.get('comment')
        code = request.POST.get('code')
        product_obj = models.Product.objects.filter(barcode=code).first()
        comment_obj = models.Comment(
            user = request.user,
            product = product_obj,
            comment = comment,
            ranking = Comment.sentiment_analysis(comment)
        )
        comment_obj.save()
        response = {"result": "success"}
        return Response(response, status=status.HTTP_200_OK)
