import jwt

def token_verify(token):
    secret_key = 'super-secret-key-please-change'
    try:
        return jwt.decode(token, secret_key, algorithm='HS256')
    except jwt.DecodeError:
        return False

token_key_authentication = hug.authentication.token(token_verify)

@hug.get('/token_authenticated', requires=token_key_authentication)  # noqa
def token_auth_call(user: hug.directives.user):
    return 'You are user: {0} with data {1}'.format(user['user'], user['data'])
