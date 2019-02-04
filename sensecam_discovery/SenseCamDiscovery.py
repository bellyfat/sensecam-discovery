"""This module is used to get the ip and the information related to
each camera on the same network."""

__version__ = '1.0.13'


import subprocess
from typing import List

import WSDiscovery
from onvif import ONVIFCamera


def discover(scope = None) -> List:
    """Discover cameras on network using onvif discovery.

    Returns:
        List: List of ips found in network.
    """
    lst = list()
    if(scope == None):
        cmd = 'hostname -I'
        scope = subprocess.check_output(cmd, shell=True).decode('utf-8')
    wsd = WSDiscovery.WSDiscovery()
    wsd.start()
    ret = wsd.searchServices()
    for service in ret:
        get_ip = str(service.getXAddrs())
        get_types = str(service.getTypes())
        for ip_scope in scope.split():
            result = get_ip.find(ip_scope.split('.')[0] + '.' + ip_scope.split('.')[1])
            if result > 0 and get_types.find('onvif') > 0:
                string_result = get_ip[result:result+13]
                string_result = string_result.split('/')[0]
                lst.append(string_result)
    wsd.stop()
    lst.sort()
    return lst


class CameraONVIF:
    """This class is used to get the information from all cameras discovered on this specific
    network."""

    def __init__(self, ip, user, password):
        """Constructor.

        Args:
            ip (str): Ip of the camera.
            user (str): Onvif login.
            password (str): Onvif password.
        """
        self._mycam = ONVIFCamera(ip, 80, user, password, no_cache = True)
        self._camera_media = self._mycam.create_media_service()
        self._camera_media_profile = self._camera_media.GetProfiles()[0]

    @property
    def hostname(self) -> str:
        """Find hostname of camera.

        Returns:
            str: Hostname.
        """
        resp = self._mycam.devicemgmt.GetHostname()
        return resp.Name

    @property
    def manufacturer(self) -> str:
        """Find manufacturer of camera.

        Returns:
            str: Manufacturer.
        """
        resp = self._mycam.devicemgmt.GetDeviceInformation()
        return resp.Manufacturer

    @property
    def model(self) -> str:
        """Find model of camera.

        Returns:
            str: Model.
        """
        resp = self._mycam.devicemgmt.GetDeviceInformation()
        return resp.Model

    @property
    def firmware_version(self) -> str:
        """Find firmware version of camera.

        Returns:
            str: Firmware version.
        """
        resp = self._mycam.devicemgmt.GetDeviceInformation()
        return resp.FirmwareVersion

    @property
    def mac_address(self) -> str:
        """Find serial number of camera.

        Returns:
            str: Serial number.
        """
        resp = self._mycam.devicemgmt.GetDeviceInformation()
        return resp.SerialNumber

    @property
    def hardware_id(self) -> str:
        """Find hardware id of camera.

        Returns:
            str: Hardware Id.
        """
        resp = self._mycam.devicemgmt.GetDeviceInformation()
        return resp.HardwareId

    @property
    def resolutions_available(self) -> List:
        """Find all resolutions of camera.

        Returns:
            tuple: List of resolutions (Width, Height).
        """
        request = self._camera_media.create_type('GetVideoEncoderConfigurationOptions')
        request.ProfileToken = self._camera_media_profile.token
        config = self._camera_media.GetVideoEncoderConfigurationOptions(request)
        return [(res.Width, res.Height) for res in config.H264.ResolutionsAvailable]

    @property
    def frame_rate_range(self) -> int:
        """Find the frame rate range of camera.

        Returns:
            int: FPS min.
            int: FPS max.
        """
        request = self._camera_media.create_type('GetVideoEncoderConfigurationOptions')
        request.ProfileToken = self._camera_media_profile.token
        config = self._camera_media.GetVideoEncoderConfigurationOptions(request)
        return config.H264.FrameRateRange.Min, config.H264.FrameRateRange.Max

    @property
    def date(self) -> str:
        """Find date configured on camera.

        Returns:
            str: Date in string.
        """
        datetime = self._mycam.devicemgmt.GetSystemDateAndTime()
        return datetime.UTCDateTime.Date

    @property
    def time(self) -> str:
        """Find local hour configured on camera.

        Returns:
            str: Hour in string.
        """
        datetime = self._mycam.devicemgmt.GetSystemDateAndTime()
        return datetime.UTCDateTime.Time

    @property
    def is_ptz(self) -> bool:
        """Check if camera is PTZ or not.

        Returns:
            bool: Is PTZ or not.
        """
        resp = self._mycam.devicemgmt.GetCapabilities()
        return bool(resp.PTZ)