import dj_database_url
import conf.settings as settings
from rc import Cache, CacheCluster

redis_conf = []
redis_conf.append(dj_database_url.parse(settings.REDIS_URL))

try:
    for ii in range(1, 10):
        redis_conf.append(j_database_url.parse(default = getattr(settings, 'REDIS_URL_%s') % (ii)))
except Exception as e:
    pass

cluster_conf = {}
for ii in range(len(redis_conf)):
    cluster_conf['cache0%s' % (ii)] = {'host': redis_conf[ii]['HOST'], 'port': redis_conf[ii]['PORT'], 'db': redis_conf[ii]['NAME'], 'password': redis_conf[ii]['PASSWORD']}

cache = CacheCluster(cluster_conf)

# cache = Cache(host='localhost',
#               port=6379,
#               db=0,
#               password=None,
#               default_expire = 24 * 3600)  # one day

if __name__ == '__main__':
    print(dir(cache))
