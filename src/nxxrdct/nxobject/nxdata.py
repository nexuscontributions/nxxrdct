"""
Module for handling the NXdata group holding the integrated data.
"""

from __future__ import annotations

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


class NXdata(NXobject):
    def __init__(self, node_name="data", parent: NXobject | None = None) -> None:
        super().__init__(node_name=node_name, parent=parent)
        self._set_freeze(False)
        self._intensity = None
        self._intensity_errors = None
        self._radial_axis = None
        self._radial_axis_long_name = None
        self._set_freeze(True)

    @property
    def intensity(self):
        """Azimuthally integrated intensity, saved as I; shape (nTrans, nRot, nRad)"""
        return self._intensity

    @intensity.setter
    def intensity(self, value):
        self._intensity = value

    @property
    def intensity_errors(self):
        """Estimated intensity errors, saved as I_errors; same shape as intensity"""
        return self._intensity_errors

    @intensity_errors.setter
    def intensity_errors(self, value):
        self._intensity_errors = value

    @property
    def radial_axis(self):
        """Radial bin centres (2theta or q); shape (nRad,)"""
        return self._radial_axis

    @radial_axis.setter
    def radial_axis(self, value):
        self._radial_axis = value

    @property
    def radial_axis_long_name(self) -> str | None:
        """Quantity of the radial axis, one of '2theta' or 'q'"""
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
        data_paths = nexus_paths.nx_data_paths
        nx_dict = {}

        if self.intensity is not None:
            path = f"{self.path}/{data_paths.INTENSITY}"
            nx_dict[path] = self.intensity
            nx_dict[f"{path}@long_name"] = "intensity"
            nx_dict[f"{path}@units"] = "arbitrary units"
            nx_dict[f"{self.path}@signal"] = data_paths.INTENSITY
            nx_dict[f"{self.path}@interpretation"] = "image"
        if self.intensity_errors is not None:
            path = f"{self.path}/{data_paths.INTENSITY_ERRORS}"
            nx_dict[path] = self.intensity_errors
            nx_dict[f"{path}@long_name"] = "estimated intensity error"
            nx_dict[f"{path}@units"] = "arbitrary units"
        if self.radial_axis is not None:
            if self.radial_axis_long_name is None:
                raise ValueError(
                    "radial_axis_long_name must be set when radial_axis is given, "
                    f"one of {tuple(RADIAL_AXIS_UNITS)}"
                )
            path = f"{self.path}/{data_paths.RADIAL_AXIS}"
            radial_axis = _coerce_radial_axis(
                self.radial_axis, self.radial_axis_long_name
            )
            nx_dict[path] = radial_axis.magnitude
            nx_dict[f"{path}@units"] = f"{radial_axis.units:~}"
            nx_dict[f"{path}@long_name"] = self.radial_axis_long_name

        if nx_dict:
            nx_dict[f"{self.path}@NX_class"] = "NXdata"
        return nx_dict

    def _load(self, file_path: str, data_path: str, nexus_version: float) -> NXobject:
        nexus_paths = get_paths(nexus_version)
        data_paths = nexus_paths.nx_data_paths

        self.intensity = get_data(
            file_path, "/".join([data_path, data_paths.INTENSITY])
        )
        self.intensity_errors = get_data(
            file_path, "/".join([data_path, data_paths.INTENSITY_ERRORS])
        )
        radial_axis_path = "/".join([data_path, data_paths.RADIAL_AXIS])
        long_name = get_attribute(file_path, radial_axis_path, "long_name")
        if long_name is not None:
            self.radial_axis_long_name = long_name
            self.radial_axis = get_quantity(
                file_path,
                radial_axis_path,
                default_unit=RADIAL_AXIS_UNITS[long_name][0],
            )
        else:
            self.radial_axis_long_name = None
            self.radial_axis = get_data(file_path, radial_axis_path)
        return self
