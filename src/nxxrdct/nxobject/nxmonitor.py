"""
Module for handling an NXmonitor.
"""

from __future__ import annotations

from nxxrdct.nxobject.nxobject import NXobject
from nxxrdct.paths.nxxrdct import get_paths
from nxxrdct.utils import get_data


class NXmonitor(NXobject):
    def __init__(self, node_name="control", parent: NXobject | None = None) -> None:
        super().__init__(node_name=node_name, parent=parent)
        self._set_freeze(False)
        self._data = None
        self._mode = None
        self._preset = None
        self._integral = None
        self._set_freeze(True)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def mode(self) -> str | None:
        return self._mode

    @mode.setter
    def mode(self, value: str | None):
        if not isinstance(value, (type(None), str)):
            raise TypeError("mode is expected to be None or str")
        self._mode = value

    @property
    def preset(self):
        return self._preset

    @preset.setter
    def preset(self, value):
        self._preset = value

    @property
    def integral(self):
        return self._integral

    @integral.setter
    def integral(self, value):
        self._integral = value

    def to_nx_dict(
        self,
        nexus_path_version: float | None = None,
        data_path: str | None = None,
    ) -> dict:
        nexus_paths = get_paths(nexus_path_version)
        monitor_paths = nexus_paths.nx_monitor_paths
        nx_dict = {}

        if self.data is not None:
            nx_dict[f"{self.path}/{monitor_paths.DATA}"] = self.data
        if self.mode is not None:
            nx_dict[f"{self.path}/{monitor_paths.MODE}"] = self.mode
        if self.preset is not None:
            nx_dict[f"{self.path}/{monitor_paths.PRESET}"] = self.preset
        if self.integral is not None:
            nx_dict[f"{self.path}/{monitor_paths.INTEGRAL}"] = self.integral

        if nx_dict:
            nx_dict[f"{self.path}@NX_class"] = "NXmonitor"
        return nx_dict

    def _load(self, file_path: str, data_path: str, nexus_version: float) -> NXobject:
        nexus_paths = get_paths(nexus_version)
        monitor_paths = nexus_paths.nx_monitor_paths
        self.data = get_data(file_path, "/".join([data_path, monitor_paths.DATA]))
        self.mode = get_data(file_path, "/".join([data_path, monitor_paths.MODE]))
        self.preset = get_data(file_path, "/".join([data_path, monitor_paths.PRESET]))
        self.integral = get_data(
            file_path, "/".join([data_path, monitor_paths.INTEGRAL])
        )
