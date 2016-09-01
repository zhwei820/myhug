#coding=utf8
#-#import json
#-#import re
from operator import itemgetter
from itsdangerous import URLSafeTimedSerializer
from itsdangerous import SignatureExpired
from itsdangerous import BadSignature
from tornado import gen
from tornado.options import options as _options
if __name__ == '__main__':
    import sys
    import os
#-#    par_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    par_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.abspath(os.path.join(par_dir, os.path.pardir)))
    import server_conf
    server_conf
from applib.verify_lib import VCManager
from applib.tools_lib import str2_int_list
#-#from lib.mysql_manager_rw import mmysql_rw
from applib.rule_lib import PromotionRuleManager
from lib.redis_manager import m_redis
from lib.rabbitmq_lib import RabbitMqLib
from applib.quest_lib import QuestManager
from lib.applog import app_log
info, debug, error = app_log.info, app_log.debug, app_log.error


class UserLib(object):
    # reg_source 取值
    REG_SOURCE_DESC = {'wx': u'微信号',
                       'qq': u'QQ号',
                       'wb': u'新浪微博号',
                       'mb': u'手机号'}
    # score_type 取值描述
    _SCORE_TYPE_DB_NAME = {0: ('', u'扣款'),
                           1: ('', u'退款'),
                           2: ('score_predeposit', u'预存'),
                           3: ('score_register', u'注册奖励'),
                           4: ('score_invite', u'邀请奖励'),
                           5: ('score_task', u'任务奖励'),
                           6: ('score_active', u'活动奖励'),
                           7: ('score_field_1', u'预留1'),
                           8: ('score_field_2', u'预留2'),
                           9: ('score_field_3', u'预留3'),
                           10: ('score_field_4', u'预留4'),
                           11: ('score_field_5', u'预留5'),
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
    def getDefaultUserScoreList(uid):
        return {'uid': uid,
                'score': 0,
                'score_charge_hbb': 0,
                'score_charge_alipay': 0,
                'score_charge_weixin': 0,
                'score_consumption': 0,
                'score_cancel_consumption': 0,
                'score_withdraw': 0,
                'score_cancel_withdraw': 0,
                'score_predeposit': 0,
                'score_register': 0,
                'score_invite': 0,
                'score_task': 0,
                'score_active': 0,
                'score_field_1': 0,
                'score_field_2': 0,
                'score_field_3': 0,
                'score_field_4': 0,
                'score_field_5': 0,
                }

    @staticmethod
    @gen.coroutine
    def close():
        pass

    @staticmethod
    @gen.coroutine
    def updateUserBasicOSTypeIfNeeded(handler, uid, os_type):
        m = handler.mysql_conn()
        sql = 'UPDATE o_user_basic SET os_type = "%s" WHERE uid = %s AND os_type != "%s";' % (os_type, uid, os_type)
        yield m.SQ(sql)

    @staticmethod
    @gen.coroutine
    def getUserInfoByUid(handler, uid):
        u'''根据 ``uid`` 获取用户信息

        **args**
         * ``uid``

        **return**
         * dict 包含key:
            * ``uid``
            * ``channel``
            * ``invite_uid``
            * ``qid``
            * ``reg_source``
            * ``bind_mobile``
            * ``nickname``
            * ``gender``
            * ``figure_url``
            * ``province``
            * ``city``
            * ``country``
        '''
        user_info = None
        c_k = '%s%s' % (m_redis._USER_INFO_, uid)
        user_info = handler.get_obj_cache(c_k)
        if not user_info:
            m = handler.mysql_conn()
            sql = "select a.uid, a.channel, a.invite_uid, a.reg_qid, a.bind_mobile, b.nickname, b.gender, b.figure_url, b.province, b.city, b.country, a.reg_source, a.ctime, a.os_type from o_user_basic a, o_user_extra b where a.uid=b.uid and a.uid=%s"
            yield m.SQ(sql, (uid,))
            rs = m.fetchone()
            if rs:
                user_info = {'uid': rs[0],
                             'channel': rs[1],
                             'invite_uid': rs[2],
                             'qid': rs[3],
                             'reg_source': rs[11],
                             'bind_mobile': rs[4],
                             'nickname': rs[5],
                             'gender': rs[6],
                             'figure_url': rs[7],
                             'province': rs[8],
                             'city': rs[9],
                             'country': rs[10],
                             'ctime': rs[12],
                             'os_type': rs[13],
                             }
                handler.set_cache_obj(c_k, user_info, 3600)
        else:
            info('cache hit %s', c_k)
        raise gen.Return(user_info)

    @staticmethod
    @gen.coroutine
    def getUserScoreByUid(handler, uid):
        u'''根据 ``uid`` 获取用户资金信息

        **return**
          dict, key: <score_type> value: <score_value>
        '''
        c_k = '%s%s' % (m_redis._SCORE_INFO_, uid)
        score_info = handler.get_obj_cache(c_k)
        if not score_info:
            m = handler.mysql_conn()
            sql = "SELECT uid, score, score_charge_hbb, score_charge_alipay, score_charge_weixin, score_consumption, score_cancel_consumption, score_withdraw, score_cancel_withdraw, score_predeposit, score_register, score_invite, score_task, score_active, score_field_1, score_field_2, score_field_3, score_field_4, score_field_5 FROM %s WHERE uid = %s;" % (UserLib._whichScoreTbl(uid), uid)
            yield m.SQ(sql)
            rs = m.fetchone()
            if rs:
                score_info = {'uid': rs[0],
                              'score': rs[1],
                              'score_charge_hbb': rs[2],
                              'score_charge_alipay': rs[3],
                              'score_charge_weixin': rs[4],
                              'score_consumption': rs[5],
                              'score_cancel_consumption': rs[6],
                              'score_withdraw': rs[7],
                              'score_cancel_withdraw': rs[8],
                              'score_predeposit': rs[9],
                              'score_register': rs[10],
                              'score_invite': rs[11],
                              'score_task': rs[12],
                              'score_active': rs[13],
                              'score_field_1': rs[14],
                              'score_field_2': rs[15],
                              'score_field_3': rs[16],
                              'score_field_4': rs[17],
                              'score_field_5': rs[18],
                              }
            else:
                # 默认值
                score_info = {'uid': int(uid),
                              'score': 0,
                              'score_charge_hbb': 0,
                              'score_charge_alipay': 0,
                              'score_charge_weixin': 0,
                              'score_consumption': 0,
                              'score_cancel_consumption': 0,
                              'score_withdraw': 0,
                              'score_cancel_withdraw': 0,
                              'score_predeposit': 0,
                              'score_register': 0,
                              'score_invite': 0,
                              'score_task': 0,
                              'score_active': 0,
                              'score_field_1': 0,
                              'score_field_2': 0,
                              'score_field_3': 0,
                              'score_field_4': 0,
                              'score_field_5': 0,
                              }
            handler.set_cache_obj(c_k, score_info, 3600)
        else:
            info('cache hit %s', c_k)
        raise gen.Return(score_info or UserLib.getDefaultUserScoreList(uid))

    @staticmethod
    @gen.coroutine
    def getUserBalance(handler, uid):
        u'''根据 ``uid`` 获取用户资金信息中的余额

        **return**
         <score or 0>
        '''
        ret = 0
        try:
            score_info = yield UserLib.getUserScoreByUid(handler, uid)
        except:
            error('获取用户资金信息失败！', exc_info=True)
        else:
            ret = score_info.get('score', 0)
        raise gen.Return(ret)

    @staticmethod
    @gen.coroutine
    def checkUserByUid(handler, uid):
        u'''判断id为 `uid` 的用户是否存在

        **return**
         <True or False>
        '''
        ret = False
        m = handler.mysql_conn()
        yield m.SQ("select uid from o_user_basic where uid=%s ", (uid,))
        rs = m.fetchone()
        if rs:
            ret = True
        raise gen.Return(ret)

    @staticmethod
    @gen.coroutine
    def getUidByQid(handler, qid, reg_source=None):
        u'''判断 `qid` 注册的用户是否存在

        **args**
         * `qid`
         * `reg_source` 可选

        **return**
         <True or False>
        '''
        ret = None
        m = handler.mysql_conn()
        if reg_source:
            sql = "select uid from o_user_basic where reg_source=%s and reg_qid=%s "
            args = (reg_source, qid)
        else:
            sql = "select uid from o_user_basic where reg_qid=%s "
            args = (qid, )

        yield m.SQ(sql, args)
        rs = m.fetchone()
        if rs:
            ret = rs[0]
        raise gen.Return(ret)

    @staticmethod
    @gen.coroutine
    def getUidByBindMobile(handler, bind_mobile, reg_source=None):
        ret = None
        m = handler.mysql_conn()
        if reg_source:
            sql = "SELECT uid FROM o_user_basic WHERE reg_source = %s AND bind_mobile = %s;"
            args = (reg_source, bind_mobile)
        else:
            sql = "SELECT uid FROM o_user_basic WHERE bind_mobile = %s;"
            args = (bind_mobile, )
        yield m.SQ(sql, args)
        rs = m.fetchone()
        if rs and rs[0]:
            ret = rs[0]
        raise gen.Return(ret)

    @staticmethod
    @gen.coroutine
    def getQidByBindMobile(handler, bind_mobile, reg_source=None):
        ret = None
        m = handler.mysql_conn()
        if reg_source:
            sql = "SELECT reg_qid FROM o_user_basic WHERE reg_source = %s AND bind_mobile = %s;"
            args = (reg_source, bind_mobile)
        else:
            sql = "SELECT reg_qid FROM o_user_basic WHERE bind_mobile = %s;"
            args = (bind_mobile, )
        yield m.SQ(sql, args)
        rs = m.fetchone()
        if rs and rs[0]:
            ret = rs[0]
        raise gen.Return(ret)

    @staticmethod
    def clearScoreCache(handler, uid):
        r = handler.get_redis()
        c_k = '%s%s' % (m_redis._SCORE_INFO_, uid)
        r.delete(c_k)

    @staticmethod
    def clearUserInfoCache(handler, uid):
#-#        r = handler.get_redis()
        c_k = '%s%s' % (m_redis._USER_INFO_, uid)
        handler.del_cache(c_k)
        c_k = '%s%s' % (m_redis._ONE_TUDI_NUM_, uid)
        handler.del_cache(c_k)
        c_k = '%s%s' % (m_redis._ONE_TUSUN_NUM_, uid)
        handler.del_cache(c_k)

    @staticmethod
    @gen.coroutine
    def addScore(handler, score_obj):
        u'''资金变更
        '''
        ret = None
        uid, device_id, event_type, event_sub_type, score, order_id, pay_id, remark, ip, os_type = \
            itemgetter('uid',
                       'device_id',
                       'event_type',
                       'event_sub_type',
                       'score',
                       'order_id',
                       'pay_id',
                       'remark',
                       'ip',
                       'os_type',
                       )(score_obj)

        try:
            assert uid and int(uid) >= 10000000
            score = int(score)
        except:
            raise gen.Return(ret)

        # 扣款、退款只加减余额和记录
        score_sql_str = ''
        if event_type not in [0, 1]:
            # 更新主表的加分类别，如果加分类别不存在则主表更新不会成功，因此出错返回
            try:
                score_str = UserLib._SCORE_TYPE_DB_NAME[event_type][0]
                assert score_str
                score_sql_str = ", %s = %s + %s" % (score_str, score_str, score)
            except:
                raise gen.Return(ret)

        m = handler.mysql_conn(UserLib._whichScoreDB(uid))
        balance = 0
        try:
            sql = "SELECT uid, score FROM %s WHERE uid = %%s" % UserLib._whichScoreTbl(uid)
            yield m.SQ(sql, (uid,))
            rs = m.fetchone()
            if not rs:
                balance = score
                rslt = yield UserLib.checkUserByUid(handler, uid)
                if rslt:
                    yield m.SQ("insert into %s (uid, score) values(%%s, %%s)" % UserLib._whichScoreTbl(uid), (uid, 0))
            else:
                balance = int(rs[1]) + score
            sql = "UPDATE %s SET score = score + %%s, update_time = now() %s WHERE uid = %%s" % (UserLib._whichScoreTbl(uid), score_sql_str)
            yield m.SQ(sql, (score, uid))
        except:
            error('', exc_info=True)
            raise gen.Return(ret)
        else:
            UserLib.clearScoreCache(handler, uid)

        # log
        try:
            # log表规则是取uid倒数第2位分库 最后1位分表 共100个表（包括0）
            sql = "INSERT INTO %s (uid, device_id, event_type, event_sub_type, score, balance, ctime, order_id, pay_id, os_type, remark, ip) " \
                  " values(%%s, %%s, %%s, %%s, %%s, %%s, now(), %%s, %%s, %%s, %%s, %%s)" % UserLib._whichScoreLogTbl(uid)
            args = (uid, m.F(device_id), m.F(str(event_type)), m.F(str(event_sub_type)), score, balance, m.F(str(order_id)), m.F(str(pay_id)), m.F(os_type), m.F(remark), ip)
            yield m.SQ(sql, args)
        except:
            error('', exc_info=True)

        raise gen.Return(ret)

    @staticmethod
    def _whichScoreDB(uid):
        return "score_%s" % str(uid)[-2]

    @staticmethod
    def _whichScoreTbl(uid):
        return "o_user_score_%s" % str(uid)[-1]
        # return "o_user_score_%s" % str(uid)[-2:]

    @staticmethod
    def _whichScoreLogTbl(uid):
        return "o_score_log_%s" % str(uid)[-2:]

    @staticmethod
    @gen.coroutine
    def addUser(handler, user_obj):
        u'''
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
        ret_uid, ret_ticket, ret_msg = None, None, ''
        reg_qid, token, reg_source, invite_uid, ip, os_type, app_version, channel, nickname, gender, figure_url, figure_url_other, province, city, country, year = user_obj['reg_qid'], user_obj['token'], user_obj['reg_source'], user_obj['invite_uid'], user_obj['ip'], user_obj['os_type'], user_obj['app_version'], user_obj['channel'], user_obj['nickname'], user_obj['gender'], user_obj['figure_url'], user_obj.get('figure_url_other', ''), user_obj['province'], user_obj['city'], user_obj['country'], user_obj.get('year', '')
        usc = handler.user_service_conn()
        # 检查邀请人
        if invite_uid:
            ret = yield usc.checkUserByUid(handler, invite_uid)
            if not ret:
                info('邀请人无效 %s', invite_uid)
                invite_uid = '0'
        else:
            invite_uid = '0'
        # 检查是否已注册
        ret = yield usc.getUidByQid(handler, reg_qid, reg_source)
        if ret:
            ret_msg = u'%s已注册，请直接登陆' % UserLib.REG_SOURCE_DESC.get(reg_source, u'')
        else:
            m = handler.mysql_conn()
            m_score = None
            reg_lck = '_lck_reg_%s' % reg_qid
            r = handler.get_redis()
            if r.incr(reg_lck) == 1:
                r.expire(reg_lck, 30)
                try:
                    try:
                        sql = "INSERT INTO o_user_basic(ctime, channel, os_type, app_version, reg_ip, invite_uid, reg_source, reg_qid, status) " \
                              "VALUES(NOW(), %s, %s, %s, %s, %s, %s, %s, %s)"
                        args = (channel, os_type, app_version, ip, invite_uid, reg_source, reg_qid, 1)
                        m.TQ(sql, args)
                        uid = m.db.insert_id()
                        assert uid
                        m_score = handler.mysql_conn(UserLib._whichScoreDB(uid))
                        if reg_source == 'mb':  # 手机号注册，昵称默认为139*****888这种（隐藏中间5位）
                            nickname = '%s*****%s' % (str(reg_qid)[:3], str(reg_qid)[-3:])
                        nickname = nickname.strip()  # 有一些用户名前后有空格或空行，处理一下
                        ticket = URLSafeTimedSerializer(_options.token_secret_key, _options.token_salt_login).dumps({'uid': uid, 'mobile': reg_qid})
                        sql = "INSERT INTO o_user_extra(uid, reg_source, reg_qid, token, ticket, nickname, gender, figure_url, figure_url_other, province, city, country, year) " \
                              "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        args = (uid, reg_source, reg_qid, token, ticket, nickname, gender, figure_url, figure_url_other, province, city, country, year or 0)
                        m.TQ(sql, args)
                        info('uid: %s, score_table: %s' % (uid, UserLib._whichScoreTbl(uid)))
                        m_score.TQ("INSERT INTO %s (uid, score, ctime, utime) VALUES(%%s, %%s, NOW(), NOW())" % UserLib._whichScoreTbl(uid), (uid, 0))
                        m.db.commit()
                        m_score.db.commit()
                    except:
                        ret_msg = u'数据库错误'
                        try:
                            m.db.rollback()
                        except:
                            pass
                        if m_score:
                            try:
                                m_score.db.rollback()
                            except:
                                pass
                        error('添加新用户时出错', exc_info=True)
                    else:  # 创建用户成功
                        info('用户注册成功 reg_qid: %s uid: %s ticket: %s', reg_qid, uid, ticket)
                        ret_uid = uid
                        ret_ticket = ticket
                        try:
                            if int(invite_uid) > 0:
                                RabbitMqLib().send_msg('task_queue', {'method': 'doQuest', 'args': {'questId': QuestManager.QUEST_TUZI_INVITE, 'uid': invite_uid, 'ulevel': 0}})  # 完成师徒邀请
                                info('用户完成徒弟邀请任务. uid %s , quest_id : %s, 被邀请人uid : %s' % (invite_uid, QuestManager.QUEST_TUZI_INVITE, uid))
                                userInfo = yield UserLib.getUserInfoByUid(handler, invite_uid)
                                if userInfo and int(userInfo['invite_uid']) > 0:
                                    RabbitMqLib().send_msg('task_queue', {'method': 'doQuest', 'args': {'questId': QuestManager.QUEST_TUSUN_INVITE, 'uid': userInfo['invite_uid'], 'ulevel': -1}})  # 完成徒孙邀请
                                    info('用户完成徒孙邀请任务. uid %s , quest_id : %s' % (userInfo['invite_uid'], QuestManager.QUEST_TUSUN_INVITE))
#-#                            RabbitMqLib().send_msg('task_queue', {'method': 'applyPromotionRule', 'args': {'event': 'reg', 'uid': uid, 'test': True}})
                            yield PromotionRuleManager.applyPromotionRule(handler, 'reg', uid, test=True)
                            handler.set_cache(m_redis._ONE_NEW_USER_FLAG_ + str(uid), '1', 86400)
                            RabbitMqLib().send_msg('task_queue', {'method': 'processUnRegShareCoupon', 'args': {'uid': uid}})
                            RabbitMqLib().send_msg('task_queue', {'method': 'createQuestList', 'args': {'uid': uid}})
                        except:
                            pass
                finally:
                    r.delete(reg_lck)
            else:
                ret_msg = u'请勿重复注册'

        raise gen.Return((ret_uid, ret_ticket, ret_msg))

    @staticmethod
    @gen.coroutine
    def getNewTicket(handler, uid, qid):
        ticket = URLSafeTimedSerializer(_options.token_secret_key, _options.token_salt_login).dumps({'uid': uid, 'mobile': qid})
        m = handler.mysql_conn()
        sql = 'update o_user_extra set ticket=%s where uid=%s'
        yield m.SQ(sql, (ticket, uid))
        raise gen.Return(ticket)

    @staticmethod
    @gen.coroutine
    def checkTicket(handler, user_obj):
        u'''验证ticket

        **args**
         * ``user_obj`` 必须包含 `reg_source` 和 `ticket` 。目前 `reg_source` 未被使用

        **return**
         (<err_code>, <err_msg>, <data_in_ticket or None>)
        '''
        err_code, err_msg, ret_data = 0, '', None
        reg_source, ticket = itemgetter('reg_source', 'ticket')(user_obj)
        sig = URLSafeTimedSerializer(_options.token_secret_key, _options.token_salt_login)
        try:
            d = sig.loads(ticket, max_age=3600 * 24 * 60)
        except BadSignature:
            err_code, err_msg = handler.err._ERR_USER_VALIDATE_WRONG, u'为保证账户安全，请重新登录'  # ticket 无效
        except SignatureExpired:
            err_code, err_msg = handler.err._ERR_USER_VALIDATE_WRONG, u'为保证账户安全，请重新登录'  # ticket 过期
        else:
            ret_data = d
        raise gen.Return((err_code, err_msg, ret_data))

    @staticmethod
    @gen.coroutine
    def validateUser(handler, user_obj):
        u'''验证用户(ticket是否有效，用户是否存在)

        **return**
          (<err_code>, <err_msg>, <uid or None>)
        '''
        err_code, err_msg, ret_data = 0, '', None
        if 'reg_source' in user_obj and 'ticket' in user_obj:
            err_code, err_msg, ret_data = yield UserLib.checkTicket(handler, user_obj)
            if ret_data:
                user_exist = yield UserLib.checkUserByUid(handler, ret_data['uid'])
                if user_exist:
                    ret_data = ret_data['uid']
                else:
                    info('用户%s不存在', ret_data['uid'])
                    ret_data = None
        else:
            err_code, err_msg = handler.err._ERR_INVALID_ARG, u'缺少登陆参数'
#-#        info('%s %s %s', err_code, err_msg, ret_data)
        raise gen.Return((err_code, err_msg, ret_data))

    @staticmethod
    @gen.coroutine
    def bindMobile(handler, ticket, mobile, vc):
        u'''第三方登陆后，绑定一个手机号
        前提：这个手机号之前没有注册过(但可以被其他第三方登陆帐号绑定过)

        **args**
         * ``ticket`` 访问凭据
         * ``mobile`` 要绑定的手机号
         * ``vc`` 验证码


        **return**
         * ``err_code``
         * ``err_msg``
        '''
        err_code, err_msg = 0, ''
        # 检查验证码
        bPassed, sErr = yield VCManager.verify(handler, '', str(mobile), vc)
        if not bPassed:
            err_code, err_msg = handler.err._ERR_COUPON_ERR, sErr
        else:
            err_code, err_msg, uid = yield UserLib.validateUser(handler, {'reg_source': '', 'ticket': ticket})
            if uid:
                m = handler.mysql_conn()
                yield m.SQ("select uid from o_user_basic where reg_source='mb' and reg_qid=%s", (uid, ))
                rcd = m.fetchone()
                if rcd:
                    info('绑定失败 手机号 %s 已经注册过 uid %s', mobile, uid)
                    err_code, err_msg = handler.err._ERR_ONE_MOBILE_ALREADY_REG, u'此手机号之前已经注册为帐号，无法进行绑定！'
                else:
                    uinfo = yield UserLib.getUserInfoByUid(handler, uid)
                    if uinfo:
                        if uinfo['bind_mobile'] != 0:
                            info('绑定失败 %s 已经绑定过手机号 %s', uid, uinfo['bind_mobile'])
                            err_code, err_msg = handler.err._ERR_ONE_ACCOUNT_ALREADY_BIND_MOBILE, u'帐号已经绑定过手机号 %s' % uinfo['bind_mobile']
                        else:
                            info('绑定成功 %s 绑定到 uid %s', mobile, uid)
                            yield m.SQ("update o_user_basic set bind_mobile=%s where uid=%s", (mobile, uid))

        raise gen.Return((err_code, err_msg))

    @staticmethod
    @gen.coroutine
    def updateNickname(handler, ticket, rs, nickname):
        u'''修改昵称
        '''
        err_code, err_msg, uid = yield UserLib.validateUser(handler, {'reg_source': rs, 'ticket': ticket})
        if uid:
            m = handler.mysql_conn()
            sql = "update o_user_extra set nickname='%s' where uid=%s;" % (nickname, uid)
            yield m.SQ(sql)
            info('修改 %s 的昵称为 %s', uid, nickname)

        raise gen.Return((err_code, err_msg))

    # 使某人成为某人的师父
    @staticmethod
    @gen.coroutine
    def makeFatherChildRelation(handler, father_uid, child_uid):
        child_info = yield UserLib.getUserInfoByUid(handler, child_uid)
        if child_info['invite_uid'] == 0:
            m = handler.mysql_conn()
            yield m.SQ('UPDATE o_user_basic SET invite_uid = %s WHERE uid = %s;', (father_uid, child_uid))
            UserLib.clearUserInfoCache(handler, child_uid)
            info('使 %s 成为 %s 的师父', father_uid, child_uid)
            RabbitMqLib().send_msg('task_queue', {'method': 'doQuest', 'args': {'questId': QuestManager.QUEST_TUZI_INVITE, 'uid': father_uid, 'ulevel': 0}})  # 完成师徒邀请
            info('用户完成徒弟邀请任务. uid %s , quest_id : %s' % (father_uid, QuestManager.QUEST_TUZI_INVITE))
            userInfo = yield UserLib.getUserInfoByUid(handler, father_uid)
            if userInfo and userInfo['invite_uid']:
                RabbitMqLib().send_msg('task_queue', {'method': 'doQuest', 'args': {'questId': QuestManager.QUEST_TUSUN_INVITE, 'uid': userInfo['invite_uid'], 'ulevel': -1}})  # 完成徒孙邀请
                info('用户完成徒孙邀请任务. uid %s , quest_id : %s' % (userInfo['invite_uid'], QuestManager.QUEST_TUSUN_INVITE))
            raise gen.Return(True)
        raise gen.Return(False)

    # 获得徒弟的数量
    @staticmethod
    @gen.coroutine
    def getTuDiNum(handler, uid):
        cache_key = m_redis._ONE_TUDI_NUM_ + str(uid)
        r = handler.get_redis()
        tudi_num = r.get(cache_key)
        if tudi_num:
            raise gen.Return(int(tudi_num))

        tudi_num = 0
        m = handler.mysql_conn('one_r')
        sql = 'SELECT COUNT(*) FROM o_user_basic WHERE invite_uid = %s AND status = 1;' % uid
        yield m.SQ(sql)
        rs = m.fetchone()
        if rs:
            tudi_num = rs[0]
            r.setex(cache_key, tudi_num, 60 * 60)
        raise gen.Return(tudi_num)

    # 获得徒孙的数量
    @staticmethod
    @gen.coroutine
    def getTuSunNum(handler, uid):
        cache_key = m_redis._ONE_TUSUN_NUM_ + str(uid)
        r = handler.get_redis()
        tusun_num = r.get(cache_key)
        if tusun_num:
            raise gen.Return(int(tusun_num))

        tusun_num = 0
        m = handler.mysql_conn('one_r')
        sql = 'SELECT COUNT(*) FROM o_user_basic WHERE invite_uid IN (SELECT uid FROM o_user_basic WHERE invite_uid = %s AND status = 1);' % uid
        yield m.SQ(sql)
        rs = m.fetchone()
        if rs:
            tusun_num = rs[0]
            r.setex(cache_key, tusun_num, 60 * 60)
        raise gen.Return(tusun_num)

    # 查询某人 师傅的师傅
    @staticmethod
    @gen.coroutine
    def getGrandparent(handler, uid):
        cache_key = m_redis._ONE_GRANDPARENT_ + str(uid)
        r = handler.get_redis()
        grandparent = r.get(cache_key)
        if grandparent:
            raise gen.Return(grandparent)

#-#        tusun_num = 0
        m = handler.mysql_conn('one_r')
        sql = 'SELECT invite_uid FROM o_user_basic WHERE uid = (SELECT invite_uid FROM o_user_basic WHERE uid = %s AND status = 1);' % uid
        yield m.SQ(sql)
        rs = m.fetchone()
        if rs:
            grandparent = rs[0]
            r.setex(cache_key, grandparent, 60 * 60)
        raise gen.Return(grandparent)

    @staticmethod
    def clear_push_cache(handler, uid, os_type):
        r = handler.get_redis()
        r_key = ('_ONE_PUSH_IOS' + str(uid)) if os_type == 'ios' else ("_ONE_PUSH_ANDROID" + str(uid))
        info("delete %s" % (r_key))
        r.delete(r_key)

    @staticmethod
    @gen.coroutine
    def checkUserVipLevel(handler, uid, vip_flag):
        u''' 判断 ``uid`` 的vip类型是否是 ``vip_flag`` 中的一种

        **arg**
         * ``uid``
         * ``vip_flag`` 要判断的类型。单独的值 UserLib.USER_VIP_TYPE_NONE  或者 USER_VIP_TYPE_INVITE / USER_VIP_TYPE_BANKER 中的一个值，多个值用 | 连接

        **return**
         * <True_or_False> 代表用户 ``uid`` 是否是 ``vip_flag`` 指定类型的一种或多种
        '''
        c_k = m_redis._ONE_VIP_LEVEL_ + str(uid)
        vip_level = handler.get_cache(c_k)
        if vip_level is None:
            try:
                m = handler.mysql_conn('one_r')
                yield m.SQ('select group_concat(distinct vip_type) from o_vip_list where uid=%s and status=1 group by uid', (uid, ))
                rs = m.fetchone()
            except:
                error('获取用户 %s 的vip类型时出错', uid, exc_info=True)
                vip_level = 0
                handler.set_cache(c_k, vip_level, 30)
            else:
                if rs:
                    vtype = rs[0]
                else:
                    vtype = ''
                vip_level = reduce(lambda x, y: x | y, str2_int_list(vtype), 0)
                handler.set_cache(c_k, vip_level, 300)
#-#        else:
#-#            info('cache hit %s', c_k)
        if vip_flag != UserLib.USER_VIP_TYPE_NONE:
            raise gen.Return((int(vip_level) & vip_flag) > 0)
        else:
            raise gen.Return(int(vip_level) == 0)


if __name__ == '__main__':
    from lib.formwork import ToolsMixin

    @gen.coroutine
    def main_test():
        handler = ToolsMixin()
#-#        usc = handler.user_service_conn()
#-#        r = yield usc.addScore(handler, {'uid': 10000000,
#-#                                         'device_id': '999',
#-#                                         'event_type': UserLib.EVENT_SCORE_REFUND,
#-#                                         'event_sub_type': 0,
#-#                                         'score': 23 * 100,
#-#                                         'order_id': '',
#-#                                         'pay_id': 0,
#-#                                         'remark': '测试充值',
#-#                                         'ip': '192.168.199.112',
#-#                                         'os_type': '',
#-#                                         })
        # r = yield UserLib.checkTicket(handler, {'reg_source': None, 'ticket': sys.argv[1]})
#-#        r = yield UserLib.getGrandparent(handler, 10080990)
#-#        r = UserLib.clear_push_cache(handler, 10000000, 'ios')
#-#        r = yield UserLib.addUser(handler, {'reg_qid': 13512345679,
#-#                                                'token': 'test_token',
#-#                                                'reg_source': 'mb',
#-#                                                'invite_uid': '',
#-#                                                'ip': '192.168.199.112',
#-#                                                'os_type': 'android',
#-#                                                'app_version': '1.3.5.7',
#-#                                                'channel': 'self_test',
#-#                                                'nickname': '',
#-#                                                'gender': '',
#-#                                                'figure_url': '',
#-#                                                'province': '',
#-#                                                'city': '',
#-#                                                'country': '',
#-#                                                }
#-#                                      )
#-#        r = yield UserLib.checkUserVipLevel(handler, 1000, UserLib.USER_VIP_TYPE_INVITE | UserLib.USER_VIP_TYPE_BANKER)
        r = yield UserLib.checkUserVipLevel(handler, 1000, UserLib.USER_VIP_TYPE_NONE)
        from applib.tools_lib import pcformat
        info('r: %s', pcformat(r))

    from tornado.ioloop import IOLoop
    IOLoop.instance().run_sync(main_test)
