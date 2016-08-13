# coding=utf-8

from lib.rc import cache
from lib.tools import tools
from lib import redisManager
from lib.logger import info, error

class VersionLib(object):
    """docstring for VersionLib"""

    @staticmethod
    @cache.cache()
    def get_version_by_id(id):
        m = tools.mysql_conn()
        m.Q("SELECT id, version, os_type, ctime, what_news, update_is_recommend, update_is_force, app_id, dl_url, channel, status FROM o_version WHERE id = %s;", (id, ))  # 参数绑定防止sql注入
        res = m.fetch_one()
        ret = {"data": res, "code": 0}
        return ret

    @staticmethod
    @cache.cache()
    def get_version_id(os_type, app_version, uid_ext):
        version_list = VersionLib.get_version_list(os_type)
        for item in version_list:
            if app_version < item['version'] and (item['rate'] == '[]' or uid_ext in json.loads(item['rate'])):
                return item['id']
        return None

    @staticmethod
    @cache.cache()
    def get_version_list(os_type):
        m = tools.mysql_conn()
        m.Q("SELECT id, version, os_type, ctime, what_news, update_is_recommend, update_is_force, app_id, dl_url, channel, status, rate FROM o_version WHERE os_type = %s ORDER BY ctime LIMIT 10;", (os_type, ))  # 参数绑定防止sql注入
        res = m.fetch_all()
        return res

    @staticmethod
    @cache.cache()
    def get_update_is_force(os_type, app_version):
        m = tools.mysql_conn()
        m.Q("SELECT update_is_force FROM o_version WHERE os_type = %s and app_version = %s;", (os_type, app_version))  # 参数绑定防止sql注入
        res = m.fetch_one()
        return True if (res and res['update_is_force']) else False

    def get_version(os_type, app_version, uid_ext):
        version_id = VersionLib.get_version_id(os_type, app_version, uid_ext)
        if version_id:
            version = VersionLib.get_version_by_id(version_id)
            version['update_is_force'] = VersionLib.get_update_is_force(os_type, app_version)
            return version
        else:
            return None
