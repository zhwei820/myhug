
from rc import Cache

cache = Cache(default_expire = 24 * 3600)  # one day

if __name__ == '__main__':
    print(dir(cache))
