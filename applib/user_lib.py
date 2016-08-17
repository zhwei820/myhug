# coding=utf-8
import jwt
import traceback
from decouple import config
from lib.rc import cache
from lib.tools import tools, http_put
from lib.logger import info, error

class UserManager(object):
    def __init__(self, arg):
        super(UserManager, self).__init__()
        self.arg = arg

    @staticmethod
    def add_user(obj):
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
        # usc = tools.user_service_conn()
        # 检查邀请人
        # if invite_uid:
        #     ret = yield usc.checkUserByUid(tools, invite_uid)
        #     if not ret:
        #         info('邀请人无效 %s', invite_uid)
        #         invite_uid = '0'
        # else:
        #     invite_uid = '0'
        # 检查是否已注册
        # ret = yield usc.getUidByQid(tools, reg_qid, reg_source)
        ret = False
        if ret:
            ret_msg = u'%s已注册，请直接登陆' % UserManager.REG_SOURCE_DESC.get(reg_source, u'')
        else:
            m = tools.mysql_conn()
            m_score = None
            reg_lck = '_lck_reg_%s' % obj['reg_qid']
            r = tools.get_redis()
            if r.incr(reg_lck) == 1:
                r.expire(reg_lck, 30)
                try:
                    try:
                        sql = "INSERT INTO o_user_basic(ctime, channel, os_type, app_version, package_name, reg_ip, invite_uid, reg_source, reg_qid, status, ) " \
                              "VALUES(NOW(), %s, %s, %s, %s, %s, %s, %s, %s, 1)"
                        args = (obj['channel'], obj['os_type'], obj['app_version'], obj['package_name'], obj['reg_ip'], obj['invite_uid'], obj['reg_source'], obj['reg_qid'])
                        m.TQ(sql, args)
                        uid = m.db.insert_id()
                        assert uid
                        m_score = tools.mysql_conn('d')
                        if reg_source == 'mb':  # 手机号注册，昵称默认为139*****888这种（隐藏中间5位）
                            nickname = '%s*****%s' % (str(obj['reg_qid'])[:3], str(obj['reg_qid'])[-3:])
                        nickname = nickname.strip()  # 有一些用户名前后有空格或空行，处理一下

                        ticket = jwt.encode({'uid': uid, 'mobile': reg_qid}, config('token_secret_key'), algorithm='HS256')
                        sql = "INSERT INTO o_user_extra(uid, reg_source, reg_qid, token, ticket, nickname, gender, figure_url, figure_url_other, province, city, country, year) " \
                              "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        args = (uid, obj['reg_source'], obj['reg_qid'], obj['token'], obj['reg_qid'], ticket, obj['nickname'], obj['gender'], obj['figure_url'], obj['figure_url_other'], obj['province'], obj['city'], obj['country'], obj['year'])
                        m.TQ(sql, args)
                        info('uid: %s, score_table: %s' % (uid, UserManager._whichScoreTbl(uid)))
                        m_score.TQ("INSERT INTO %s (uid, score) VALUES(%%s, %%s)" % UserManager._whichScoreTbl(uid), (uid, 0))
                        m.db.commit()
                        m_score.db.commit()
                    except:
                        traceback.print_exc()
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
                        # try:
                        #     if invite_uid:
                        #         RabbitMqLib().send_msg('task_queue', {'method': 'doQuest', 'args': {'questId': QuestManager.QUEST_TUZI_INVITE, 'uid': invite_uid, 'ulevel': 0}})  # 完成师徒邀请
                        #         info('用户完成徒弟邀请任务. uid %s , quest_id : %s, 被邀请人uid : %s' % (invite_uid, QuestManager.QUEST_TUZI_INVITE, uid))
                        #         userInfo = yield UserManager.getUserInfoByUid(tools, invite_uid)
                        #         if userInfo and userInfo['invite_uid']:
                        #             RabbitMqLib().send_msg('task_queue', {'method': 'doQuest', 'args': {'questId': QuestManager.QUEST_TUSUN_INVITE, 'uid': userInfo['invite_uid'], 'ulevel': -1}})  # 完成徒孙邀请
                        #             info('用户完成徒孙邀请任务. uid %s , quest_id : %s' % (userInfo['invite_uid'], QuestManager.QUEST_TUSUN_INVITE))
                        #     RabbitMqLib().send_msg('task_queue', {'method': 'applyPromotionRule', 'args': {'event': 'reg', 'uid': uid, 'test': True}})
                        #     RabbitMqLib().send_msg('task_queue', {'method': 'processUnRegShareCoupon', 'args': {'uid': uid}})
                        #     RabbitMqLib().send_msg('task_queue', {'method': 'createQuestList', 'args': {'uid': uid}})
                        # except:
                        #     pass
                finally:
                    r.delete(reg_lck)
            else:
                ret_msg = u'请勿重复注册'

        return (ret_uid, ret_ticket, ret_msg)
