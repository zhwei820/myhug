from tasks import *
a = sum_test.delay(num=3)
a.wait()
print(a.result)
#
# a = sum_test.delay('q3')
# print(a.result)
