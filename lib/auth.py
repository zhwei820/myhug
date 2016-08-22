import jwt
import hug

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


def token_authorization(request):
    """Token verification

    Checks for the Authorization header and verifies using the validate_ticket function
    """
    token = request.get_header('Authorization')
    if token:
        return validate_ticket(token)
    return None
