from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

class AliyunMessage:

    client = AcsClient('', '', '')

    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https') # https | http
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')

    # request.add_query_param('RegionId', "cn-hangzhou")
    # request.add_query_param('PhoneNumbers', "18616730743")
    # request.add_query_param('SignName', "光阴")
    # request.add_query_param('TemplateCode', "SMS_189830981")
    # request.add_query_param('TemplateParam', "{\"code\":\"169101\"}")

    response = client.do_action_with_exception(request)
    print(str(response, encoding = 'utf-8'))