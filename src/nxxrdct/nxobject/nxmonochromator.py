"""
Module for handling an NXmonochromator.
"""

from __future__ import annotations

import pint

from nxxrdct.nxobject.nxobject import NXobject
from nxxrdct.paths.nxxrdct import get_paths
from nxxrdct.utils import get_quantity

_ureg = pint.get_application_registry()


class NXmonochromator(NXobject):
    def __init__(
        self, node_name="monochromator", parent: NXobject | None = None
    ) -> None:
        super().__init__(node_name=node_name, parent=parent)
        self._set_freeze(False)
        self._wavelength = None
        self._set_freeze(True)

    @property
    def wavelength(self) -> pint.Quantity | None:
        return self._wavelength

    @wavelength.setter
    def wavelength(self, value):
        if value is None:
            self._wavelength = None
        elif isinstance(value, pint.Quantity):
            self._wavelength = value.to(_ureg.angstrom)
        else:
            self._wavelength = _ureg.Quantity(value, _ureg.angstrom)

    def to_nx_dict(
        self,
        nexus_path_version: float | None = None,
        data_path: str | None = None,
    ) -> dict:
        nexus_paths = get_paths(nexus_path_version)
        mono_paths = nexus_paths.nx_monochromator_paths
        nx_dict = {}

        if self.wavelength is not None:
            path = f"{self.path}/{mono_paths.WAVELENGTH}"
            nx_dict[path] = self.wavelength.magnitude
            nx_dict[f"{path}@units"] = f"{self.wavelength.units:~}"

        if nx_dict:
            nx_dict[f"{self.path}@NX_class"] = "NXmonochromator"
        return nx_dict

    def _load(self, file_path: str, data_path: str, nexus_version: float) -> NXobject:
        nexus_paths = get_paths(nexus_version)
        mono_paths = nexus_paths.nx_monochromator_paths
        self.wavelength = get_quantity(
            file_path,
            "/".join([data_path, mono_paths.WAVELENGTH]),
            default_unit=_ureg.angstrom,
        )
