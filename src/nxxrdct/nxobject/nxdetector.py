"""
Module for handling an NXdetector.
"""

from __future__ import annotations

import warnings

import numpy
import pint

from nxxrdct.nxobject.nxobject import NXobject
from nxxrdct.paths.nxxrdct import get_paths
from nxxrdct.utils import get_attribute
from nxxrdct.utils import get_data
from nxxrdct.utils import get_quantity

_ureg = pint.get_application_registry()

# first unit of each entry is the default
RADIAL_AXIS_UNITS = {
    "2theta": (_ureg.degree, _ureg.radian),
    "q": ((1 / _ureg.angstrom).units, (1 / _ureg.nanometer).units),
}


def _coerce_quantity(value, unit: pint.Unit):
    if value is None:
        return None
    if isinstance(value, pint.Quantity):
        return value
    return numpy.asarray(value) * unit


def _coerce_radial_axis(value, long_name: str) -> pint.Quantity:
    """Keep supported units as given; convert other compatible units to the default."""
    supported_units = RADIAL_AXIS_UNITS[long_name]
    quantity = _coerce_quantity(value, supported_units[0])
    if quantity.units in supported_units:
        return quantity
    try:
        return quantity.to(supported_units[0])
    except pint.DimensionalityError as err:
        raise ValueError(
            f"radial_axis units '{quantity.units}' are incompatible "
            f"with radial_axis_long_name {long_name!r} "
            f"(expected one of {tuple(str(unit) for unit in supported_units)})"
        ) from err


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
        self._radial_axis = None
        self._radial_axis_long_name = None
        self._set_freeze(True)

    @property
    def data(self):
        """Azimuthally integrated intensity on a regular grid;
        shape (nTrans, nRot, nRadialBins)"""
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

    # --- Deprecate diffraction_channel ---
    @property
    def diffraction_channel(self):
        return self._radial_axis

    @diffraction_channel.setter
    def diffraction_channel(self, value):
        warnings.warn(
            "'diffraction_channel' is deprecated; use 'radial_axis' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._radial_axis = value

    @property
    def radial_axis(self):
        return self._radial_axis

    @radial_axis.setter
    def radial_axis(self, value):
        self._radial_axis = value

    @property
    def radial_axis_long_name(self) -> str | None:
        return self._radial_axis_long_name

    @radial_axis_long_name.setter
    def radial_axis_long_name(self, value: str | None):
        if value is not None and value not in RADIAL_AXIS_UNITS:
            raise ValueError(
                "radial_axis_long_name must be one of "
                f"{tuple(RADIAL_AXIS_UNITS)}, got {value!r}"
            )
        self._radial_axis_long_name = value

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
            polar_angle = self.polar_angle.to(_ureg.degree)
            nx_dict[path] = polar_angle.magnitude
            nx_dict[f"{path}@units"] = f"{polar_angle.units:~}"
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
        if self.radial_axis is not None:
            if self.radial_axis_long_name is None:
                raise ValueError(
                    "radial_axis_long_name must be set when radial_axis is given, "
                    f"one of {tuple(RADIAL_AXIS_UNITS)}"
                )
            path = f"{self.path}/{detector_paths.RADIAL_AXIS}"
            radial_axis = _coerce_radial_axis(
                self.radial_axis, self.radial_axis_long_name
            )
            nx_dict[path] = radial_axis.magnitude
            nx_dict[f"{path}@units"] = f"{radial_axis.units:~}"
            # silx shows long_name in place of the units, so the label carries them
            nx_dict[f"{path}@long_name"] = (
                f"{self.radial_axis_long_name} ({radial_axis.units:~})"
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
        radial_axis_path = "/".join([data_path, detector_paths.RADIAL_AXIS])
        long_name = get_attribute(file_path, radial_axis_path, "long_name")
        if long_name is not None:
            self.radial_axis_long_name = long_name.split(" (")[0]
            self.radial_axis = get_quantity(
                file_path,
                radial_axis_path,
                default_unit=RADIAL_AXIS_UNITS[self.radial_axis_long_name][0],
            )
        else:
            self.radial_axis_long_name = None
            self.radial_axis = get_data(file_path, radial_axis_path)
