import jwt
import hug

# def token_verify(ticket):
#     secret_key = 'super-secret-key-please-change'
#     try:
#         res = jwt.decode(ticket, secret_key, algorithm='HS256')
#         return res
#     except jwt.DecodeError:
#         return False

# token_key_authentication = hug.authentication.token(token_verify)

# @hug.get('/_authenticated', requires=token_key_authentication)  # noqa
# def _authenticated():
#     return 'hug'


def get_new_ticket(uid, qid, rs):
    ticket = jwt.encode({'uid': uid, 'qid': qid, 'reg_source': rs}, config('token_secret_key'), algorithm='HS256')
    return ticket

def validate_ticket(ticket):
    res = None
    try:
        res = jwt.decode(ticket, config('token_secret_key'), algorithm='HS256')
    except Exception as e:
        return None
    if res and res['uid']:
        return True
    else:
        return False


def authenticator(function, challenges=()):
    """Wraps authentication logic, verify_user through to the authentication function.

    The verify_user function passed in should accept an API key and return a user object to
    store in the request context if authentication succeeded.
    """
    challenges = challenges or ('{} realm="simple"'.format(function.__name__), )

    def wrapper(verify_user):
        def authenticate(request, response, **kwargs):
            result = function(request, response, verify_user, **kwargs)
            if result is None:
                raise HTTPUnauthorized('Authentication Required',
                                       'Please provide valid {0} credentials'.format(function.__doc__.splitlines()[0]),
                                       challenges=challenges)

            if result is False:
                raise HTTPUnauthorized('Invalid Authentication',
                                       'Provided {0} credentials were invalid'.format(function.__doc__.splitlines()[0]),
                                       challenges=challenges)

            request.context['user'] = result
            return True

        authenticate.__doc__ = function.__doc__
        return authenticate

    return wrapper


@authenticator
def basic(request, response, verify_user, realm='simple', **kwargs):
    """Basic HTTP Authentication"""
    http_auth = request.auth
    response.set_header('WWW-Authenticate', 'Basic')
    if http_auth is None:
        return

    if isinstance(http_auth, bytes):
        http_auth = http_auth.decode('utf8')
    try:
        auth_type, user_and_key = http_auth.split(' ', 1)
    except ValueError:
        raise HTTPUnauthorized('Authentication Error',
                               'Authentication header is improperly formed',
                               challenges=('Basic realm="{}"'.format(realm), ))

    if auth_type.lower() == 'basic':
        try:
            user_id, key = base64.decodebytes(bytes(user_and_key.strip(), 'utf8')).decode('utf8').split(':', 1)
            user = verify_user(user_id, key)
            if user:
                response.set_header('WWW-Authenticate', '')
                return user
        except (binascii.Error, ValueError):
            raise HTTPUnauthorized('Authentication Error',
                                   'Unable to determine user and password with provided encoding',
                                   challenges=('Basic realm="{}"'.format(realm), ))
    return False


@authenticator
def token_authorization():
    """Token verification

    Checks for the Authorization header and verifies using the validate_ticket function
    """
    token = request.get_header('Authorization')
    if token:
        return validate_ticket(token)
    return None
