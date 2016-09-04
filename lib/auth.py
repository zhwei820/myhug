# coding=utf-8
import jwt
import hug
from decouple import config
from itsdangerous import URLSafeTimedSerializer
from itsdangerous import SignatureExpired
from itsdangerous import BadSignature

def check_ticket(ticket):
    u'''验证ticket

    **args**
     * ``user_obj`` 必须包含 `reg_source` 和 `ticket` 。目前 `reg_source` 未被使用

    **return**
     (<code>, <message>, <data_in_ticket or None>)
    '''
    code, message, ret = 0, '', None
    sig = URLSafeTimedSerializer(config('token_secret_key'))
    try:
        res = sig.loads(ticket, max_age = 3600 * 24 * 60)
    except BadSignature:
        return (handler.err._ERR_USER_VALIDATE_WRONG, '为保证账户安全，请重新登录', ret)  # ticket 无效
    except SignatureExpired:
        return (handler.err._ERR_USER_VALIDATE_WRONG, '为保证账户安全，请重新登录', ret)  # ticket 过期
    else:
        return (code, message, ret)

def get_new_ticket(uid, qid):
    ticket = URLSafeTimedSerializer(config('token_secret_key')).dumps({'uid': uid, 'qid': qid})
    return ticket
