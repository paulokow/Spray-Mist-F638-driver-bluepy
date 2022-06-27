from spraymistf638.driver import *
from unittest.mock import patch, MagicMock
import pytest


def test_create_driver():
    dr = SprayMistF638("1:1:1:1:1:1")
    assert False == dr.connected


def test_connect():
    with patch("spraymistf638.driver.Peripheral") as mocked_ble:
        mocked_ble.getServiceByUUID.return_value = MagicMock()

        dr = SprayMistF638("1:1:1:1:1:1")
        assert True == dr.connect()
        assert True == dr.connected

        dr2 = SprayMistF638("1:1:1:1:1:1")
        dr2._device.connect.side_effect = BTLEException("Test exception")
        # connect throws
        assert False == dr2.connect()
        assert False == dr2.connected


def test_disconnect():
    with patch("spraymistf638.driver.Peripheral") as mocked_ble:
        mocked_ble.getServiceByUUID.return_value = MagicMock()

        dr = SprayMistF638("1:1:1:1:1:1")
        # if already disconnected, returns true
        assert True == dr.disconnect()
        # connect
        assert True == dr.connect()
        assert True == dr.connected
        # disconnect
        assert True == dr.disconnect()
        assert False == dr.connected
        # if already disconnected, returns true
        assert True == dr.disconnect()

        dr2 = SprayMistF638("1:1:1:1:1:1")
        dr2._device.disconnect.side_effect = BTLEException("Test exception")
        # connect
        assert True == dr2.connect()
        assert True == dr2.connected
        # disconnect throws
        assert False == dr2.disconnect()
        assert False == dr2.connected


def test_get_working_mode():
    with patch("spraymistf638.driver.Peripheral") as mocked_ble:
        srv = MagicMock()

        dr = SprayMistF638("1:1:1:1:1:1")
        dr._device.getServiceByUUID.side_effect = (
            lambda uuid: srv
            if uuid == "0000fcc0-0000-1000-8000-00805f9b34fb"
            else MagicMock()
        )
        char_mock = MagicMock()
        srv.getCharacteristics.return_value = [char_mock]
        char_mock.supportsRead.return_value = True
        char_mock.read.return_value = bytes.fromhex("520101")
        assert WorkingMode.Auto == dr.working_mode
        assert True == dr.connected
        char_mock.read.return_value = bytes.fromhex("520100")
        assert WorkingMode.Manual == dr.working_mode
        with pytest.raises(SprayMistF638Exception):
            srv.getCharacteristics.return_value = []
            res = dr.working_mode
        srv.getCharacteristics.return_value = [char_mock]
        with pytest.raises(SprayMistF638Exception):
            char_mock.read.return_value = bytes.fromhex("520103")
            res = dr.working_mode
        with pytest.raises(SprayMistF638Exception):
            char_mock.read.side_effect = BTLEException("Test exception")
            res = dr.working_mode
            assert False == dr.connected


def test_get_running_mode():
    with patch("spraymistf638.driver.Peripheral") as mocked_ble:
        srv = MagicMock()

        dr = SprayMistF638("1:1:1:1:1:1")
        dr._device.getServiceByUUID.side_effect = (
            lambda uuid: srv
            if uuid == "0000fcc0-0000-1000-8000-00805f9b34fb"
            else MagicMock()
        )
        char_mock = MagicMock()
        srv.getCharacteristics.return_value = [char_mock]
        char_mock.supportsRead.return_value = True
        char_mock.read.return_value = bytes.fromhex("610101")
        assert RunningMode.Off == dr.running_mode
        assert True == dr.connected
        char_mock.read.return_value = bytes.fromhex("610102")
        assert RunningMode.Stopped == dr.running_mode
        char_mock.read.return_value = bytes.fromhex("610104")
        assert RunningMode.RunningAutomatic == dr.running_mode
        char_mock.read.return_value = bytes.fromhex("61010A")
        assert RunningMode.RunningManual == dr.running_mode
        char_mock.read.return_value = bytes.fromhex("610109")
        assert RunningMode.RunningManual == dr.running_mode
        with pytest.raises(SprayMistF638Exception):
            srv.getCharacteristics.return_value = []
            res = dr.running_mode
        srv.getCharacteristics.return_value = [char_mock]
        with pytest.raises(SprayMistF638Exception):
            char_mock.read.return_value = bytes.fromhex("610103")
            res = dr.running_mode
        with pytest.raises(SprayMistF638Exception):
            char_mock.read.side_effect = BTLEException("Test exception")
            res = dr.running_mode
            assert False == dr.connected


def test_get_property():
    with patch("spraymistf638.driver.Peripheral") as mocked_ble:
        srv = "0000fcc0-0000-1000-8000-00805f9b34fb"
        srv_mock = MagicMock()

        dr = SprayMistF638("1:1:1:1:1:1")
        dr._device.getServiceByUUID.side_effect = (
            lambda uuid: srv_mock if uuid == srv else MagicMock()
        )
        char_mock = MagicMock()
        srv_mock.getCharacteristics.return_value = [char_mock]
        char_mock.supportsRead.return_value = True
        char_mock.read.return_value = bytes.fromhex("520101")
        assert bytes.fromhex("520101") == dr._get_property(srv, "dummy")
        assert True == dr.connected

        char_mock.supportsRead.return_value = False
        assert None == dr._get_property(srv, "dummy")
        char_mock.supportsRead.return_value = True

        srv_mock.getCharacteristics.return_value = []
        assert None == dr._get_property(srv, "dummy")
        srv_mock.getCharacteristics.return_value = [char_mock, char_mock]
        assert None == dr._get_property(srv, "dummy")
        srv_mock.getCharacteristics.return_value = [char_mock]
        assert bytes.fromhex("520101") == dr._get_property(srv, "dummy")

        char_mock.read.side_effect = BTLEException("Test exception")
        res = dr._get_property(srv, "dummy")
        assert False == dr.connected


def test_get_battery_level():
    with patch("spraymistf638.driver.Peripheral") as mocked_ble:
        srv = MagicMock()

        dr = SprayMistF638("1:1:1:1:1:1")
        dr._device.getServiceByUUID.side_effect = (
            lambda uuid: srv
            if uuid == "0000180f-0000-1000-8000-00805f9b34fb"
            else MagicMock()
        )
        char_mock = MagicMock()
        srv.getCharacteristics.return_value = [char_mock]
        char_mock.supportsRead.return_value = True
        char_mock.read.return_value = bytes.fromhex("24")
        assert 36 == dr.battery_level
        assert True == dr.connected

        char_mock.read.return_value = bytes.fromhex("00")
        assert 0 == dr.battery_level

        char_mock.read.return_value = bytes.fromhex("64")
        assert 100 == dr.battery_level

        with pytest.raises(SprayMistF638Exception):
            srv.getCharacteristics.return_value = []
            res = dr.battery_level

        with pytest.raises(SprayMistF638Exception):
            char_mock.read.side_effect = BTLEException("Test exception")
            res = dr.battery_level
            assert False == dr.connected


def test_get_manual():
    with patch("spraymistf638.driver.Peripheral") as mocked_ble:
        srv = MagicMock()

        dr = SprayMistF638("1:1:1:1:1:1")
        dr._device.getServiceByUUID.side_effect = (
            lambda uuid: srv
            if uuid == "0000fcc0-0000-1000-8000-00805f9b34fb"
            else MagicMock()
        )

        char_mock = MagicMock()
        srv.getCharacteristics.return_value = [char_mock]
        char_mock.supportsRead.return_value = True
        char_mock.read.return_value = bytes.fromhex("690300001E")
        assert 30 == dr.manual_time
        assert False == dr.manual_on
        assert True == dr.connected
        srv.getCharacteristics.assert_called_with(
            "0000fcd9-0000-1000-8000-00805f9b34fb"
        )

        char_mock.read.return_value = bytes.fromhex("690301012C")
        assert 300 == dr.manual_time
        assert True == dr.manual_on
        assert True == dr.connected

        with pytest.raises(SprayMistF638Exception):
            srv.getCharacteristics.return_value = []
            res = dr.manual_on

        with pytest.raises(SprayMistF638Exception):
            char_mock.read.side_effect = BTLEException("Test exception")
            res = dr.manual_on
            assert False == dr.connected

        with pytest.raises(SprayMistF638Exception):
            srv.getCharacteristics.return_value = []
            res = dr.manual_time

        with pytest.raises(SprayMistF638Exception):
            char_mock.read.side_effect = BTLEException("Test exception")
            res = dr.manual_time
            assert False == dr.connected


def test_write_manual():
    with patch("spraymistf638.driver.Peripheral") as mocked_ble:
        srv = MagicMock()

        dr = SprayMistF638("1:1:1:1:1:1")
        dr._device.getServiceByUUID.side_effect = (
            lambda uuid: srv
            if uuid == "0000fcc0-0000-1000-8000-00805f9b34fb"
            else MagicMock()
        )
        char_mock = MagicMock()
        srv.getCharacteristics.return_value = [char_mock]
        char_mock.supportsRead.return_value = True
        char_mock.read.return_value = bytes.fromhex("690300001E")
        char_mock.write.return_value = {"rsp": ["wr"]}
        assert True == dr.switch_manual_on(60)
        char_mock.write.assert_called_once_with(bytes.fromhex("690301003C"), True)
        assert True == dr.connected
        char_mock.read.return_value = bytes.fromhex("690301003C")
        assert True == dr.manual_on
        char_mock.read.return_value = bytes.fromhex("6903010010")
        char_mock.write.reset_mock()
        assert True == dr.switch_manual_on()
        char_mock.write.assert_called_once_with(bytes.fromhex("690301003C"), True)

        assert True == dr.switch_manual_on(20)
        char_mock.write.reset_mock()
        assert True == dr.switch_manual_off()
        char_mock.write.assert_called_once_with(bytes.fromhex("6903000014"), True)

        srv.getCharacteristics.return_value = []
        assert False == dr.switch_manual_on()
        srv.getCharacteristics.return_value = [char_mock]

        char_mock.write.side_effect = BTLEException("Test exception")
        assert False == dr.switch_manual_on()
        assert False == dr.switch_manual_off()


def test_get_pause_days():
    with patch("spraymistf638.driver.Peripheral") as mocked_ble:
        srv = MagicMock()

        dr = SprayMistF638("1:1:1:1:1:1")
        dr._device.getServiceByUUID.side_effect = (
            lambda uuid: srv
            if uuid == "0000fcc0-0000-1000-8000-00805f9b34fb"
            else MagicMock()
        )

        char_mock = MagicMock()
        srv.getCharacteristics.return_value = [char_mock]
        char_mock.supportsRead.return_value = True
        char_mock.read.return_value = bytes.fromhex("660100")
        assert 0 == dr.pause_days
        assert True == dr.connected
        srv.getCharacteristics.assert_called_with(
            "0000fcd6-0000-1000-8000-00805f9b34fb"
        )

        char_mock.read.return_value = bytes.fromhex("660107")
        assert 7 == dr.pause_days
        assert True == dr.connected

        with pytest.raises(SprayMistF638Exception):
            srv.getCharacteristics.return_value = []
            res = dr.pause_days

        with pytest.raises(SprayMistF638Exception):
            char_mock.read.side_effect = BTLEException("Test exception")
            res = dr.pause_days
            assert False == dr.connected


def test_set_pause_days():
    with patch("spraymistf638.driver.Peripheral") as mocked_ble:
        srv = MagicMock()

        dr = SprayMistF638("1:1:1:1:1:1")
        dr._device.getServiceByUUID.side_effect = (
            lambda uuid: srv
            if uuid == "0000fcc0-0000-1000-8000-00805f9b34fb"
            else MagicMock()
        )
        char_mock = MagicMock()
        srv.getCharacteristics.return_value = [char_mock]
        char_mock.supportsRead.return_value = True
        char_mock.read.return_value = bytes.fromhex("660100")
        char_mock.write.return_value = {"rsp": ["wr"]}
        assert True == dr.set_pause_days(7)
        char_mock.write.assert_called_once_with(bytes.fromhex("660107"), True)
        assert True == dr.connected
        char_mock.read.return_value = bytes.fromhex("660107")
        assert 7 == dr.pause_days
        char_mock.write.reset_mock()
        assert True == dr.set_pause_days(0)
        char_mock.write.assert_called_once_with(bytes.fromhex("660100"), True)

        srv.getCharacteristics.return_value = []
        assert False == dr.set_pause_days(7)
        srv.getCharacteristics.return_value = [char_mock]

        char_mock.write.side_effect = BTLEException("Test exception")
        assert False == dr.set_pause_days(7)
