import json, base64, requests
from Crypto.Cipher import AES
from datetime import datetime

class AESTestClass:
    def __init__(self, plain_txt, key):
        # iv, block_size 값은 고정
        self.iv = 'jvHJ1EFA0IXBrxxz'
        self.block_size = 16
        self.plain_txt = plain_txt
        self.key = key

    def pad(self):
        # PKCS#7 패딩
        number_of_bytes_to_pad = self.block_size - len(self.plain_txt) % self.block_size
        ascii_str = chr(number_of_bytes_to_pad)
        padding_str = number_of_bytes_to_pad * ascii_str
        return self.plain_txt + padding_str

    def encrypt(self):
        cipher = AES.new(self.key.encode('utf-8'), AES.MODE_CBC, self.iv.encode('utf-8'))
        padded_txt = self.pad()
        encrypted_bytes = cipher.encrypt(padded_txt.encode('utf-8'))
        # URL-safe Base64
        encrypted_str = base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
        return encrypted_str
    
def call_access_token(MAC_ADDRESS, API_KEY, CLIENT_ID):
    # 맥주소
    mac = (MAC_ADDRESS or "").strip().strip('"').strip("'").upper().replace(":", "-")
    if not mac:
        raise SystemExit("MAC_ADDRESS가 비어있음")

    # datetime 생성
    dt = datetime.now().strftime('%Y%m%d%H%M%S')

    # JSON 페이로드 생성
    payload = {
        "mac_address": mac,
        "datetime": dt
    }
    plain_json = json.dumps(payload, separators=(',', ':'))

    # AES 암호화 → Base64
    aes = AESTestClass(plain_txt=plain_json, key=API_KEY)
    b64_cipher = aes.encrypt()

    # 인코딩 + 토큰 요청
    endpoint = "https://apigateway.kisti.re.kr/tokenrequest.do"
    params = {
        "accounts": b64_cipher,
        "client_id": CLIENT_ID
    }

    response = requests.get(endpoint, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    token = data['access_token'] 
    return token