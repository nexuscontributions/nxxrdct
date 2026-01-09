"""
Module for handling an NXsample.
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


class NXsample(NXobject):
    def __init__(self, node_name="sample", parent: NXobject | None = None) -> None:
        super().__init__(node_name=node_name, parent=parent)
        self._set_freeze(False)
        self._name = None
        self._rotation_angle = None
        self._translation_values = None
        self._x_translation = None
        self._y_translation = None
        self._z_translation = None
        self._set_freeze(True)

    @property
    def name(self) -> str | None:
        return self._name

    @name.setter
    def name(self, name: str | None) -> None:
        if not isinstance(name, (type(None), str)):
            raise TypeError(f"name is expected to be None or str not {type(name)}")
        self._name = name

    @property
    def rotation_angle(self) -> pint.Quantity | None:
        return self._rotation_angle

    @rotation_angle.setter
    def rotation_angle(self, rotation_angle):
        self._rotation_angle = _coerce_quantity(rotation_angle, _ureg.degree)

    @property
    def translation_values(self):
        return self._translation_values

    @translation_values.setter
    def translation_values(self, value):
        self._translation_values = _coerce_quantity(value, _ureg.meter)

    @property
    def x_translation(self) -> pint.Quantity | None:
        return self._x_translation

    @x_translation.setter
    def x_translation(self, value):
        self._x_translation = _coerce_quantity(value, _ureg.meter)

    @property
    def y_translation(self) -> pint.Quantity | None:
        return self._y_translation

    @y_translation.setter
    def y_translation(self, value):
        self._y_translation = _coerce_quantity(value, _ureg.meter)

    @property
    def z_translation(self) -> pint.Quantity | None:
        return self._z_translation

    @z_translation.setter
    def z_translation(self, value):
        self._z_translation = _coerce_quantity(value, _ureg.meter)

    def to_nx_dict(
        self,
        nexus_path_version: float | None = None,
        data_path: str | None = None,
    ) -> dict:
        nexus_paths = get_paths(nexus_path_version)
        sample_paths = nexus_paths.nx_sample_paths
        nx_dict = {}

        if self.name is not None:
            nx_dict[f"{self.path}/{sample_paths.NAME}"] = self.name
        if self.rotation_angle is not None:
            path = f"{self.path}/{sample_paths.ROTATION_ANGLE}"
            nx_dict[path] = self.rotation_angle.to(_ureg.degree).magnitude
            nx_dict[f"{path}@units"] = "degree"
        if self.translation_values is not None:
            path = f"{self.path}/{sample_paths.TRANSLATION_VALUES}"
            nx_dict[path] = self.translation_values.magnitude
            nx_dict[f"{path}@units"] = f"{self.translation_values.units:~}"
        if self.x_translation is not None:
            path = f"{self.path}/{sample_paths.X_TRANSLATION}"
            nx_dict[path] = self.x_translation.magnitude
            nx_dict[f"{path}@units"] = f"{self.x_translation.units:~}"
        if self.y_translation is not None:
            path = f"{self.path}/{sample_paths.Y_TRANSLATION}"
            nx_dict[path] = self.y_translation.magnitude
            nx_dict[f"{path}@units"] = f"{self.y_translation.units:~}"
        if self.z_translation is not None:
            path = f"{self.path}/{sample_paths.Z_TRANSLATION}"
            nx_dict[path] = self.z_translation.magnitude
            nx_dict[f"{path}@units"] = f"{self.z_translation.units:~}"

        if nx_dict:
            nx_dict[f"{self.path}@NX_class"] = "NXsample"
        return nx_dict

    def _load(self, file_path: str, data_path: str, nexus_version: float) -> NXobject:
        nexus_paths = get_paths(nexus_version)
        sample_paths = nexus_paths.nx_sample_paths

        self.name = get_data(file_path, "/".join([data_path, sample_paths.NAME]))
        self.rotation_angle = get_quantity(
            file_path,
            "/".join([data_path, sample_paths.ROTATION_ANGLE]),
            default_unit=_ureg.degree,
        )
        self.translation_values = get_quantity(
            file_path,
            "/".join([data_path, sample_paths.TRANSLATION_VALUES]),
            default_unit=_ureg.meter,
        )
        self.x_translation = get_quantity(
            file_path,
            "/".join([data_path, sample_paths.X_TRANSLATION]),
            default_unit=_ureg.meter,
        )
        self.y_translation = get_quantity(
            file_path,
            "/".join([data_path, sample_paths.Y_TRANSLATION]),
            default_unit=_ureg.meter,
        )
        self.z_translation = get_quantity(
            file_path,
            "/".join([data_path, sample_paths.Z_TRANSLATION]),
            default_unit=_ureg.meter,
        )
