import asyncio
from applib.user_lib import UserLib

loop = asyncio.get_event_loop()

async def _test_get_new_ticket():
    uid = 10000000
    res = await UserLib.get_user_info_by_uid(uid)
    salt = res['salt'] if res else ''
    res = await UserLib.get_new_ticket(uid, '15810538098')
    print(res)

async def _test_check_ticket():
    res = await UserLib.check_ticket('eyJ1aWQiOjEwMDAwMDAwLCJxaWQiOiIxNTgxMDUzODA5OCJ9.Cq3LVA.Cj-xAUb5ipibHbW89ISKcPGl56w', 10000000)
    print(res)


def test_get_new_ticket():
    print(loop.run_until_complete(_test_get_new_ticket()))

def test_check_ticket():
    print(loop.run_until_complete(_test_check_ticket()))
