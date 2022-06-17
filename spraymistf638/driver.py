from bluepy.btle import Peripheral, Service, Characteristic, UUID, BTLEException
import enum
import struct
from typing import Union

WATER_TIMER_SERVICE_UUID = "0000fcc0-0000-1000-8000-00805f9b34fb"
CHAR_UUID_PATTERN = "0000{}-0000-1000-8000-00805f9b34fb"
CHAR_ID_WORKING_MODE = "fcc2"
CHAR_ID_RUNNING_MODE = "fcd1"


class WorkingMode(enum.Enum):
    Manual = 0
    Auto = 1


class RunningMode(enum.Enum):
    Off = 0
    Stopped = 1
    RunningManual = 2
    RunningAutomatic = 3


class SprayMistF638Exception(Exception):
    pass


class SprayMistF638:
    def __init__(self, mac: str) -> None:
        self._mac = mac
        self._device = Peripheral()
        self._servicesloaded = False
        self._connected = False

    def connect(self) -> bool:
        if not self._connected:
            try:
                self._device.connect(self._mac)
                self._connected = True
                if not self._servicesloaded:
                    self._load_services()
                return True
            except BTLEException:
                return False
        else:
            return True

    def disconnect(self) -> bool:
        if self._connected:
            try:
                self._device.disconnect()
                self._connected = False
                return True
            except BTLEException:
                return False
        else:
            return True

    @property
    def connected(self) -> bool:
        return self._connected

    def _load_services(self) -> None:
        self._watertimerserviceint = self._device.getServiceByUUID(
            WATER_TIMER_SERVICE_UUID
        )
        self._servicesloaded = True

    @property
    def _watertimerservice(self) -> Service:
        if not self._servicesloaded:
            self.connect()
        return self._watertimerserviceint

    def _get_property(self, service: Service, uuid: str) -> Union[bytes, None]:
        if self.connect():
            try:
                chr = service.getCharacteristics(uuid)
                if len(chr) == 1:
                    if chr[0].supportsRead():
                        return chr[0].read()
            except BTLEException:
                self.disconnect()
        return None

    @property
    def working_mode(self) -> WorkingMode:
        val = self._get_property(
            self._watertimerservice, CHAR_UUID_PATTERN.format(CHAR_ID_WORKING_MODE)
        )
        if val is not None:
            res = struct.unpack("xxB", val)[0]
            if res == 0x00:
                return WorkingMode.Manual
            elif res == 0x01:
                return WorkingMode.Auto
            else:
                raise SprayMistF638Exception(f"Unknown working mode: {res}")

        else:
            raise SprayMistF638Exception(f"No characteristics returned")

    @property
    def running_mode(self) -> RunningMode:
        val = self._get_property(
            self._watertimerservice, CHAR_UUID_PATTERN.format(CHAR_ID_RUNNING_MODE)
        )
        if val is not None:
            res = struct.unpack("xxB", val)[0]
            if res == 0x01:
                return RunningMode.Off
            elif res == 0x02:
                return RunningMode.Stopped
            elif res == 0x04:
                return RunningMode.RunningAutomatic
            elif res == 0x0A:
                return RunningMode.RunningManual
            else:
                raise SprayMistF638Exception(f"Unknown running mode: {res}")
        else:
            raise SprayMistF638Exception(f"No characteristics returned")
