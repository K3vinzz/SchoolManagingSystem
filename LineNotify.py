import os
import requests


CALLBACK_URI = "https://3454-2001-b011-3814-9a0d-c4fe-391c-887a-fc17.ngrok-free.app/callback"
# CLIENT_ID = os.environ.get("client_id")
# CLIENT_SECRET = os.environ.get("client_secret")
CLIENT_ID = "0ImmPOIuEacm5nZkIUlyUd"
CLIENT_SECRET = "bHei6b7e2NFn70v2Ms8xLvLdFGW0FZe2jvO4KbLUBIG"


def Generate_auth_link(user_id):
    end_point = "https://notify-bot.line.me/oauth/authorize"
    line_oauth_url = f'{end_point}?client_id={CLIENT_ID}&scope=notify&redirect_uri={CALLBACK_URI}&response_type=code&state={user_id}'
    return line_oauth_url


def Get_access_token(code):
    end_point = "https://notify-bot.line.me/oauth/token"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded"
    }
    request_params = {
        'grant_type': "authorization_code",
        'code': code,
        'redirect_uri': CALLBACK_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(url=end_point, headers=headers, params=request_params)
    return response.json()


def Push_message(token, message):
    end_point = "https://notify-api.line.me/api/notify"
    headers = {
        'Authorization': f"Bearer {token}"
    }
    data = {
        'message': message
    }
    response = requests.post(url=end_point, headers=headers, data=data)
    return response.status_code
