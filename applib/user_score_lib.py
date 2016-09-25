import traceback
from lib.redis_cache import cache
from lib.tools import tools, http_put
from lib.logger import info, error
import lib.err_code as err_code

class UserScoreLib(object):
    # score_type 取值描述
    _SCORE_TYPE_NAME = {0: ('', '扣款'),
                       1: ('', '退款'),
                       2: ('score_predeposit', '预存'),
                       3: ('score_register', '注册奖励'),
                       4: ('score_invite', '邀请奖励'),
                       5: ('score_task', '任务奖励'),
                       6: ('score_active', '活动奖励'),
                       7: ('score_field_1', '预留1'),
                       8: ('score_field_2', '预留2'),
                       9: ('score_field_3', '预留3'),
                       10: ('score_field_4', '预留4'),
                       11: ('score_field_5', '预留5'),
                       }

    EVENT_SCORE_PAY = 0
    EVENT_SCORE_REFUND = 1
    EVENT_SCORE_PRE_DEPOSIT = 2
    EVENT_SCORE_REGISTER = 3
    EVENT_SCORE_INVITE = 4
    EVENT_SCORE_TASK = 5
    EVENT_SCORE_ACTIVE = 6
