"""
Module for handling an NXbeam.
"""

from __future__ import annotations

import pint

from nxxrdct.nxobject.nxobject import NXobject
from nxxrdct.paths.nxxrdct import get_paths
from nxxrdct.utils import get_quantity

_ureg = pint.get_application_registry()


class NXbeam(NXobject):
    def __init__(self, node_name="beam", parent: NXobject | None = None) -> None:
        super().__init__(node_name=node_name, parent=parent)
        self._set_freeze(False)
        self._incident_energy = None
        self._set_freeze(True)

    @property
    def incident_energy(self) -> pint.Quantity | None:
        return self._incident_energy

    @incident_energy.setter
    def incident_energy(self, value):
        if value is None:
            self._incident_energy = None
        elif isinstance(value, pint.Quantity):
            self._incident_energy = value.to(_ureg.keV)
        else:
            self._incident_energy = _ureg.Quantity(value, _ureg.keV)

    def to_nx_dict(
        self,
        nexus_path_version: float | None = None,
        data_path: str | None = None,
    ) -> dict:
        nexus_paths = get_paths(nexus_path_version)
        beam_paths = nexus_paths.nx_beam_paths
        nx_dict = {}

        if self.incident_energy is not None:
            path = f"{self.path}/{beam_paths.INCIDENT_ENERGY}"
            nx_dict[path] = self.incident_energy.magnitude
            nx_dict[f"{path}@units"] = f"{self.incident_energy.units:~}"

        if nx_dict:
            nx_dict[f"{self.path}@NX_class"] = "NXbeam"
        return nx_dict

    def _load(self, file_path: str, data_path: str, nexus_version: float) -> NXobject:
        nexus_paths = get_paths(nexus_version)
        beam_paths = nexus_paths.nx_beam_paths
        self.incident_energy = get_quantity(
            file_path,
            "/".join([data_path, beam_paths.INCIDENT_ENERGY]),
            default_unit=_ureg.keV,
        )
        return self
