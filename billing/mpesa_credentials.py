import requests
import json
from request.auth import HTTPBasicAuth
import base64
from datetime import datetime


class MpesaC2bCredential:
    consumer_key = "NQqCWc1BoOXPGIwXVezaaoAJGOGvbRtA"
    consumer_secret = "kX5TTTGh2hCZhuGr"
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"


class MpesaAccesstoken:
    r = requests.get(MpesaC2bCredential.api_url, auth=HTTPBasicAuth(MpesaC2bCredential.consumer_key,
                                                                    MpesaC2bCredential.consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token['access_token']


class LipanaMpesaPassword:
    lipa_time = datetime.now().strftime("%Y%m%d%H%M%S")
    business_short_code = "174379"
    Test_c2b_shortcode = "600344"
    passkey = ""
    data_to_encode = business_short_code+passkey+lipa_time
    online_password = base64.b64encode(data_to_encode.encode())
    decode_password = online_password.decode('utf-8')
