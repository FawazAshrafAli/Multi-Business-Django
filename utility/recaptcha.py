import requests

def verify_recaptcha_v3(token):
        secret_key = '6LcfGcYrAAAAANJEkKtPhBuLW-9ZUKgjbyAcf8ID'
        data = {
            'secret': secret_key,
            'response': token
        }

        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()        

        # Example: Check for score threshold
        return result.get('success') and result.get('score', 0) >= 0.5