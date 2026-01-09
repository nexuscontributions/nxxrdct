"""
Module for handling an NXdetector.
"""

from __future__ import annotations

import numpy
import pint

from nxxrdct.nxobject.nxobject import NXobject
from nxxrdct.paths.nxxrdct import get_paths
from nxxrdct.utils import get_data, get_quantity

_ureg = pint.get_application_registry()


def _coerce_quantity(value, unit: pint.Unit):
    if value is None:
        return None
    if isinstance(value, pint.Quantity):
        return value
    return numpy.asarray(value) * unit


class NXdetector(NXobject):
    def __init__(self, node_name="detector", parent: NXobject | None = None) -> None:
        super().__init__(node_name=node_name, parent=parent)
        self._set_freeze(False)
        self._data = None
        self._polar_angle = None
        self._count_time = None
        self._distance = None
        self._x_pixel_size = None
        self._y_pixel_size = None
        self._diffraction_channel = None
        self._set_freeze(True)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def polar_angle(self):
        return self._polar_angle

    @polar_angle.setter
    def polar_angle(self, value):
        self._polar_angle = _coerce_quantity(value, _ureg.degree)

    @property
    def count_time(self) -> pint.Quantity | None:
        return self._count_time

    @count_time.setter
    def count_time(self, value):
        self._count_time = _coerce_quantity(value, _ureg.second)

    @property
    def distance(self) -> pint.Quantity | None:
        return self._distance

    @distance.setter
    def distance(self, value):
        self._distance = _coerce_quantity(value, _ureg.meter)

    @property
    def x_pixel_size(self) -> pint.Quantity | None:
        return self._x_pixel_size

    @x_pixel_size.setter
    def x_pixel_size(self, value):
        self._x_pixel_size = _coerce_quantity(value, _ureg.meter)

    @property
    def y_pixel_size(self) -> pint.Quantity | None:
        return self._y_pixel_size

    @y_pixel_size.setter
    def y_pixel_size(self, value):
        self._y_pixel_size = _coerce_quantity(value, _ureg.meter)

    @property
    def diffraction_channel(self):
        return self._diffraction_channel

    @diffraction_channel.setter
    def diffraction_channel(self, value):
        self._diffraction_channel = value

    def to_nx_dict(
        self,
        nexus_path_version: float | None = None,
        data_path: str | None = None,
    ) -> dict:
        nexus_paths = get_paths(nexus_path_version)
        detector_paths = nexus_paths.nx_detector_paths
        nx_dict = {}

        if self.data is not None:
            nx_dict[f"{self.path}/{detector_paths.DATA}"] = self.data
        if self.polar_angle is not None:
            path = f"{self.path}/{detector_paths.POLAR_ANGLE}"
            nx_dict[path] = self.polar_angle.to(_ureg.degree).magnitude
            nx_dict[f"{path}@units"] = "degree"
        if self.count_time is not None:
            path = f"{self.path}/{detector_paths.COUNT_TIME}"
            nx_dict[path] = self.count_time.magnitude
            nx_dict[f"{path}@units"] = f"{self.count_time.units:~}"
        if self.distance is not None:
            path = f"{self.path}/{detector_paths.DISTANCE}"
            nx_dict[path] = self.distance.magnitude
            nx_dict[f"{path}@units"] = f"{self.distance.units:~}"
        if self.x_pixel_size is not None:
            path = f"{self.path}/{detector_paths.X_PIXEL_SIZE}"
            nx_dict[path] = self.x_pixel_size.magnitude
            nx_dict[f"{path}@units"] = f"{self.x_pixel_size.units:~}"
        if self.y_pixel_size is not None:
            path = f"{self.path}/{detector_paths.Y_PIXEL_SIZE}"
            nx_dict[path] = self.y_pixel_size.magnitude
            nx_dict[f"{path}@units"] = f"{self.y_pixel_size.units:~}"
        if self.diffraction_channel is not None:
            nx_dict[f"{self.path}/{detector_paths.DIFFRACTION_CHANNEL}"] = (
                self.diffraction_channel
            )

        if nx_dict:
            nx_dict[f"{self.path}@NX_class"] = "NXdetector"
        return nx_dict

    def _load(self, file_path: str, data_path: str, nexus_version: float) -> NXobject:
        nexus_paths = get_paths(nexus_version)
        detector_paths = nexus_paths.nx_detector_paths

        self.data = get_data(file_path, "/".join([data_path, detector_paths.DATA]))
        self.polar_angle = get_quantity(
            file_path,
            "/".join([data_path, detector_paths.POLAR_ANGLE]),
            default_unit=_ureg.degree,
        )
        self.count_time = get_quantity(
            file_path,
            "/".join([data_path, detector_paths.COUNT_TIME]),
            default_unit=_ureg.second,
        )
        self.distance = get_quantity(
            file_path,
            "/".join([data_path, detector_paths.DISTANCE]),
            default_unit=_ureg.meter,
        )
        self.x_pixel_size = get_quantity(
            file_path,
            "/".join([data_path, detector_paths.X_PIXEL_SIZE]),
            default_unit=_ureg.meter,
        )
        self.y_pixel_size = get_quantity(
            file_path,
            "/".join([data_path, detector_paths.Y_PIXEL_SIZE]),
            default_unit=_ureg.meter,
        )
        self.diffraction_channel = get_data(
            file_path,
            "/".join([data_path, detector_paths.DIFFRACTION_CHANNEL]),
        )
