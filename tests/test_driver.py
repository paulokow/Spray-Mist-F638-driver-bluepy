from spraymistf638.driver import *


def test_create_driver():
    dr = SprayMistF638("1:1:1:1:1:1")
    assert False == dr.connected
