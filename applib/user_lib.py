# coding=utf-8
import jwt
import traceback
from decouple import config
from lib.rc import cache
from lib.tools import tools, http_put
from lib.logger import info, error
import lib.err_code as err_code

class UserManager(object):
    # reg_source 取值
    REG_SOURCE_DESC = {'wx': '微信号',
                       'qq': 'QQ号',
                       'wb': '新浪微博号',
                       'mb': '手机号'}
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

    # 用户VIP类型
    USER_VIP_TYPE_NONE = 0  # 不是VIP
    USER_VIP_TYPE_INVITE = 1  # 邀请狂人
    USER_VIP_TYPE_BANKER = 2  # 庄家

    @staticmethod
    def add_user(obj):
        '''
        **args**
         * `reg_qid` 注册id 即微信/qq/微博的openid或者手机号
         * `token`
         * `reg_source` 注册模式 wx:微信 qq:QQ，wb:新浪微博 mb:手机号
         * `invite_uid` 邀请uid
         * `ip` 注册ip
         * `os_type` os类型
         * `app_version` 注册来自的app版本号
         * `channel` 渠道
         * `nickname`
         * `gender`
         * `figure_url`
         * `figure_url_other` 其他头像
         * `province`
         * `city`
         * `country`
         * `year` 出生年

        **return**
         (<`uid`>, <`ticket`>, <`msg`>)

        '''
        ret = {'uid': None, 'ticket': None, 'message': '', 'code': 0}
        # 检查邀请人
        if obj['invite_uid']:
            res = UserManager.check_user_by_uid(obj['invite_uid'])
            if not res:
                info('邀请人无效 %s', obj['invite_uid'])
                obj['invite_uid'] = '0'
        else:
            obj['invite_uid'] = '0'
        # 检查是否已注册
        res = UserManager.get_uid_by_qid(obj['reg_qid'], obj['reg_source'])
        if res:
            ret['message'] = '%s已注册，请直接登陆' % UserManager.REG_SOURCE_DESC.get(obj['reg_source'], '')
            ret['code'] = err_code._ERR_ALREADY_REGISTERED
            return ret

        m = tools.mysql_conn()
        m_score = None
        reg_lck = '_lck_reg_%s' % obj['reg_qid']
        r = tools.get_redis()

        try:
            sql = "INSERT INTO o_user_basic(ctime, channel, os_type, app_version, package_name, reg_ip, invite_uid, reg_source, reg_qid, status) " \
                  "VALUES(NOW(), %s, %s, %s, %s, %s, %s, %s, %s, 1)"
            args = (obj['channel'], obj['os_type'], obj['app_version'], obj['package_name'], obj['reg_ip'], obj['invite_uid'], obj['reg_source'], obj['reg_qid'])
            m.TQ(sql, args)
            uid = m.db.insert_id()
            assert uid
            m_score = tools.mysql_conn('d')
            if obj['reg_source'] == 'mb':  # 手机号注册，昵称默认为139*****888这种（隐藏中间5位）
                obj['nickname'] = '%s*****%s' % (str(obj['reg_qid'])[:3], str(obj['reg_qid'])[-3:])
            obj['nickname'] = obj['nickname'].strip()  # 有一些用户名前后有空格或空行，处理一下

            ticket = jwt.encode({'uid': uid, 'mobile': obj['reg_qid']}, config('token_secret_key'), algorithm='HS256')
            sql = "INSERT INTO o_user_extra(uid, reg_source, reg_qid, token, ticket, nickname, gender, figure_url, figure_url_other, province, city, country, year) " \
                  "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            args = (uid, obj['reg_source'], obj['reg_qid'], obj['token'], ticket, obj['nickname'], obj['gender'], obj['figure_url'], obj['figure_url_other'], obj['province'], obj['city'], obj['country'], obj['year'])
            m.TQ(sql, args)
            info('uid: %s, score_table: %s' % (uid, UserManager._which_score_table(uid)))
            m_score.TQ("INSERT INTO %s (uid, score) VALUES(%%s, %%s)" % UserManager._which_score_table(uid), (uid, 0))
            m.db.commit()
            m_score.db.commit()
        except:
            traceback.print_exc()
            try:
                m.db.rollback()
            except:
                pass
            if m_score:
                try:
                    m_score.db.rollback()
                except:
                    pass
            error('数据库错误, 添加新用户时出错', exc_info=True)
            ret['message'] = '注册失败'
            ret['code'] = err_code._ERR_REGISTERED_ERROR
            return ret

        info('用户注册成功 reg_qid: %s uid: %s ticket: %s', obj['reg_qid'], uid, ticket)
        ret['uid'] = uid
        ret['ticket'] = ticket
        return ret
        # try:
        #     if invite_uid:
        #         RabbitMqLib().send_msg('task_queue', {'method': 'doQuest', 'args': {'questId': QuestManager.QUEST_TUZI_INVITE, 'uid': invite_uid, 'ulevel': 0}})  # 完成师徒邀请
        #         info('用户完成徒弟邀请任务. uid %s , quest_id : %s, 被邀请人uid : %s' % (invite_uid, QuestManager.QUEST_TUZI_INVITE, uid))
        #         userInfo = UserManager.getUserInfoByUid(invite_uid)
        #         if userInfo and userInfo['invite_uid']:
        #             RabbitMqLib().send_msg('task_queue', {'method': 'doQuest', 'args': {'questId': QuestManager.QUEST_TUSUN_INVITE, 'uid': userInfo['invite_uid'], 'ulevel': -1}})  # 完成徒孙邀请
        #             info('用户完成徒孙邀请任务. uid %s , quest_id : %s' % (userInfo['invite_uid'], QuestManager.QUEST_TUSUN_INVITE))
        #     RabbitMqLib().send_msg('task_queue', {'method': 'applyPromotionRule', 'args': {'event': 'reg', 'uid': uid, 'test': True}})
        #     RabbitMqLib().send_msg('task_queue', {'method': 'processUnRegShareCoupon', 'args': {'uid': uid}})
        #     RabbitMqLib().send_msg('task_queue', {'method': 'createQuestList', 'args': {'uid': uid}})
        # except:
        #     pass

    @staticmethod
    def check_user_by_uid(uid):
        '''判断id为 `uid` 的用户是否存在
        **return**
         <True or False>
        '''
        ret = False
        m = tools.mysql_conn()
        m.Q("SELECT uid FROM o_user_basic WHERE uid = %s ", (uid,))
        rs = m.fetchone()
        if rs:
            ret = True
        return ret

    @staticmethod
    def get_uid_by_qid(qid, reg_source=None):
        u'''判断 `qid` 注册的用户是否存在
        **args**
         * `qid`
         * `reg_source` 可选
        **return**
         <True or False>
        '''
        ret = None
        m = tools.mysql_conn()
        if reg_source:
            sql = "SELECT uid FROM o_user_basic WHERE reg_source = %s AND reg_qid = %s "
            args = (reg_source, qid)
        else:
            sql = "SELECT uid FROM o_user_basic WHERE reg_qid=%s "
            args = (qid, )
        m.Q(sql, args)
        rs = m.fetchone()
        if rs:
            ret = rs['uid']
        return ret

    @staticmethod
    def get_uid_by_bind_mobile(bind_mobile, reg_source=None):
        ret = None
        m = tools.mysql_conn()
        if reg_source:
            sql = "SELECT uid FROM o_user_basic WHERE reg_source = %s AND bind_mobile = %s;"
            args = (reg_source, bind_mobile)
        else:
            sql = "SELECT uid FROM o_user_basic WHERE bind_mobile = %s;"
            args = (bind_mobile, )
        m.Q(sql, args)
        rs = m.fetchone()
        if rs and rs['uid']:
            ret = rs['uid']
        return ret

    @staticmethod
    def get_qid_by_bind_mobile(bind_mobile, reg_source=None):
        ret = None
        m = tools.mysql_conn()
        if reg_source:
            sql = "SELECT reg_qid FROM o_user_basic WHERE reg_source = %s AND bind_mobile = %s;"
            args = (reg_source, bind_mobile)
        else:
            sql = "SELECT reg_qid FROM o_user_basic WHERE bind_mobile = %s;"
            args = (bind_mobile, )
        m.Q(sql, args)
        rs = m.fetchone()
        if rs and rs['reg_qid']:
            ret = rs['reg_qid']
        return ret


    @staticmethod
    def _which_score_table(uid):
        return "o_user_score_%s" % str(uid)[-1]
        # return "o_user_score_%s" % str(uid)[-2:]

    @staticmethod
    def _which_score_log_table(uid):
        return "o_score_log_%s" % str(uid)[-2:]
