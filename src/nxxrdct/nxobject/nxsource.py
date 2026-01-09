"""
Module for handling an NXsource.
"""

from __future__ import annotations

from nxxrdct.nxobject.nxobject import NXobject
from nxxrdct.paths.nxxrdct import get_paths
from nxxrdct.utils import get_data


class NXsource(NXobject):
    def __init__(self, node_name="source", parent: NXobject | None = None) -> None:
        super().__init__(node_name=node_name, parent=parent)
        self._set_freeze(False)
        self._name = None
        self._type = None
        self._probe = None
        self._set_freeze(True)

    @property
    def name(self) -> str | None:
        return self._name

    @name.setter
    def name(self, value: str | None):
        if not isinstance(value, (type(None), str)):
            raise TypeError("name is expected to be None or str")
        self._name = value

    @property
    def type(self) -> str | None:
        return self._type

    @type.setter
    def type(self, value: str | None):
        if not isinstance(value, (type(None), str)):
            raise TypeError("type is expected to be None or str")
        self._type = value

    @property
    def probe(self) -> str | None:
        return self._probe

    @probe.setter
    def probe(self, value: str | None):
        if not isinstance(value, (type(None), str)):
            raise TypeError("probe is expected to be None or str")
        self._probe = value

    def to_nx_dict(
        self,
        nexus_path_version: float | None = None,
        data_path: str | None = None,
    ) -> dict:
        nexus_paths = get_paths(nexus_path_version)
        source_paths = nexus_paths.nx_source_paths
        nx_dict = {}

        if self.name is not None:
            nx_dict[f"{self.path}/{source_paths.NAME}"] = self.name
        if self.type is not None:
            nx_dict[f"{self.path}/{source_paths.TYPE}"] = self.type
        if self.probe is not None:
            nx_dict[f"{self.path}/{source_paths.PROBE}"] = self.probe

        if nx_dict:
            nx_dict[f"{self.path}@NX_class"] = "NXsource"
        return nx_dict

    def _load(self, file_path: str, data_path: str, nexus_version: float) -> NXobject:
        nexus_paths = get_paths(nexus_version)
        source_paths = nexus_paths.nx_source_paths

        self.name = get_data(file_path, "/".join([data_path, source_paths.NAME]))
        self.type = get_data(file_path, "/".join([data_path, source_paths.TYPE]))
        self.probe = get_data(file_path, "/".join([data_path, source_paths.PROBE]))
