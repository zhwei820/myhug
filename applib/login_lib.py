

class LoginLib(object):
    def login_weixin(self, usc, callback, post_data, reg_source, invite_uid, ip, os_type, app_version, channel, package_name):
        try:
            code = post_data.get('code', '')
            assert code
        except:
            self.writeS(None, self.err._ERR_INVALID_ARG, u'参数不正确', callback)
            return

        access_token, user_info, err_code, err_msg = await WXLoginManager.getOAuthUserInfoByCode(code, package_name)
        if err_code or not user_info:
            self.writeS(None, self.err._ERR_ONE_LOGIN_ERROR_, err_msg or u'第三方登录失败，请稍后再试', callback)
            return

        await self.login_oauth_common(usc, callback, user_info['openid'], reg_source, access_token, invite_uid, ip, os_type, app_version, channel, user_info['nickname'], ('', 'M', 'F')[user_info['sex']], user_info['headimgurl'], '', user_info['province'], user_info['city'], user_info['country'], '', package_name)


    def login_qq(self, usc, callback, post_data, reg_source, invite_uid, ip, os_type, app_version, channel, package_name):
        try:
            access_token = post_data.get('access_token', '')
            openid = post_data.get('openid', '')
        except:
            self.writeS(None, self.err._ERR_INVALID_ARG, u'参数不正确', callback)
            return

        user_info, err_code, err_msg = await QQLoginManager.getOAuthUserInfo(access_token, openid, package_name)
        if err_code or not user_info:
            self.writeS(None, self.err._ERR_ONE_LOGIN_ERROR_, err_msg or u'第三方登录失败，请稍后再试', callback)
            return

        await self.login_oauth_common(usc, callback, openid, reg_source, access_token, invite_uid, ip, os_type, app_version, channel, user_info['nickname'], self.get_qq_gender(user_info['gender']), user_info['figureurl'], mmysql_rw.F(json.dumps(self.get_qq_other_figure_url(user_info))), user_info['province'], user_info['city'], user_info.get('country', ''), user_info['year'], package_name)


    def login_wb(self, usc, callback, post_data, reg_source, invite_uid, ip, os_type, app_version, channel, package_name):
        try:
            access_token = post_data.get('access_token', '')
            uid = post_data.get('uid', '')
        except:
            self.writeS(None, self.err._ERR_INVALID_ARG, u'参数不正确', callback)
            return

        user_info, err_code, err_msg = await WBLoginManager.getOAuthUserInfo(access_token, uid)
        if err_code or not user_info:
            self.writeS(None, self.err._ERR_ONE_LOGIN_ERROR_, err_msg or u'第三方登录失败，请稍后再试', callback)
            return

        await self.login_oauth_common(usc, callback, uid, reg_source, access_token, invite_uid, ip, os_type, app_version, channel, user_info['screen_name'], self.get_wb_gender(user_info['gender']), user_info['profile_image_url'], mmysql_rw.F(json.dumps(self.get_wb_other_figure_url(user_info))), user_info['province'], user_info['city'], user_info.get('country', ''), '', package_name)


    def login_oauth_common(self, usc, callback, qid, reg_source, access_token, invite_uid, ip, os_type, app_version, channel, nickname, gender, figure_url, figure_url_other, province, city, country, year, package_name):
        uid = await UserLib.getUidByQid(self, qid, reg_source)
        if not uid:  # 不存在，添加
            uid, ticket, err_msg = await self.add_user(usc, qid, access_token, reg_source, invite_uid, ip, os_type, app_version, channel, nickname, gender, figure_url, figure_url_other, province, city, country, year)
            if not uid:
                info('添加用户失败 qid %s, os %s, err_msg: %s', qid, os_type, err_msg)
                self.writeS(None, self.err._ERR_ONE_LOGIN_ERROR_, err_msg or u'登录失败，请稍后再试', callback)
                return
        else:  # 更新 ticket
            ticket = await usc.getNewTicket(self, uid, qid)

        if os_type == 'ios' or os_type == 'android':
            await UserLib.updateUserBasicOSTypeIfNeeded(self, uid, os_type)
            UserLib.clear_push_cache(self, uid, os_type)
            await ByproductManager.update_package_name(self, uid, package_name, os_type)  # 更新package_name
        await self.login_return_common(usc, uid, ticket, callback)


    def login_return_common(self, usc, uid, ticket, callback):
        user_info = {}
        if uid:
            user_info = await usc.getUserInfoByUid(self, uid)
        if user_info:
            conf = self.get_sys_config()
            user_info['ic_url'] = conf.get('share_url', '')
            user_info['ticket'] = ticket
            UserLib.clear_push_cache(self, uid, user_info['os_type'])
            self.writeS(user_info, call_back=callback, errcode=0)
        else:
            self.writeS(None, self.err._ERR_ONE_LOGIN_ERROR_, u'登录失败，请稍后再试', callback)


    def add_user(self, usc, openid, access_token, reg_source, invite_uid, ip, os_type, app_version, channel, nickname, gender, figure_url, figure_url_other, province, city, country, year):
        uid, ticket, err_msg = await usc.addUser(self, {
            'reg_qid': openid,
            'token': access_token,
            'reg_source': reg_source,
            'invite_uid': invite_uid,
            'ip': ip,
            'os_type': os_type,
            'app_version': app_version,
            'channel': channel,
            'nickname': nickname,
            'gender': gender,
            'figure_url': figure_url,
            'figure_url_other': figure_url_other or '',
            'province': province,
            'city': city,
            'country': country,
            'year': year or ''})
        raise gen.Return((uid, ticket, err_msg))

    def get_qq_gender(self, qq_gender):
        return {'男': 'M', '女': 'F'}.get(qq_gender, '')

    def get_qq_other_figure_url(self, user_info):
        return {
            'figure_url_1': user_info['figureurl_1'],
            'figure_url_2': user_info['figureurl_2'],
            'figure_url_qq_1': user_info['figureurl_qq_1'],
            'figure_url_qq_2': user_info['figureurl_qq_2']
        }

    def get_wb_gender(self, wb_gender):
        return {'m': 'M', 'f': 'F'}.get(wb_gender, '')

    def get_wb_other_figure_url(self, user_info):
        return {
            'avatar_large': user_info['avatar_large'],
            'avatar_hd': user_info['avatar_hd']
        }
