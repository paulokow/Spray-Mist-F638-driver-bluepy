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
        assert True == dr2.connected


def test_get_working_mode():
    with patch("spraymistf638.driver.Peripheral") as mocked_ble:
        srv = MagicMock()

        dr = SprayMistF638("1:1:1:1:1:1")
        dr._device.getServiceByUUID.return_value = srv
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
        dr._device.getServiceByUUID.return_value = srv
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
        with pytest.raises(SprayMistF638Exception):
            srv.getCharacteristics.return_value = []
            res = dr.running_mode
        srv.getCharacteristics.return_value = [char_mock]
        with pytest.raises(SprayMistF638Exception):
            char_mock.read.return_value = bytes.fromhex("61010C")
            res = dr.running_mode
        with pytest.raises(SprayMistF638Exception):
            char_mock.read.side_effect = BTLEException("Test exception")
            res = dr.running_mode
            assert False == dr.connected


def test_get_property():
    with patch("spraymistf638.driver.Peripheral") as mocked_ble:
        srv = MagicMock()

        dr = SprayMistF638("1:1:1:1:1:1")
        dr._device.getServiceByUUID.return_value = srv
        char_mock = MagicMock()
        srv.getCharacteristics.return_value = [char_mock]
        char_mock.supportsRead.return_value = True
        char_mock.read.return_value = bytes.fromhex("520101")
        assert bytes.fromhex("520101") == dr._get_property(srv, "dummy")
        assert True == dr.connected

        char_mock.supportsRead.return_value = False
        assert None == dr._get_property(srv, "dummy")
        char_mock.supportsRead.return_value = True

        srv.getCharacteristics.return_value = []
        assert None == dr._get_property(srv, "dummy")
        srv.getCharacteristics.return_value = [char_mock, char_mock]
        assert None == dr._get_property(srv, "dummy")
        srv.getCharacteristics.return_value = [char_mock]
        assert bytes.fromhex("520101") == dr._get_property(srv, "dummy")

        char_mock.read.side_effect = BTLEException("Test exception")
        res = dr._get_property(srv, "dummy")
        assert False == dr.connected
