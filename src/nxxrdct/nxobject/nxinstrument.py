"""
Module for handling an NXinstrument.
"""

from __future__ import annotations

from nxxrdct.nxobject.nxdetector import NXdetector
from nxxrdct.nxobject.nxmonochromator import NXmonochromator
from nxxrdct.nxobject.nxobject import NXobject
from nxxrdct.nxobject.nxsource import NXsource
from nxxrdct.paths.nxxrdct import get_paths
from nxxrdct.utils import get_data


class NXinstrument(NXobject):
    def __init__(self, node_name="instrument", parent: NXobject | None = None) -> None:
        super().__init__(node_name=node_name, parent=parent)
        self._set_freeze(False)
        self._name = None
        self._detector = NXdetector(node_name="detector", parent=self)
        self._source = NXsource(node_name="source", parent=self)
        self._monochromator = NXmonochromator(node_name="monochromator", parent=self)
        self._set_freeze(True)

    @property
    def name(self) -> str | None:
        return self._name

    @name.setter
    def name(self, value: str | None) -> None:
        if not isinstance(value, (type(None), str)):
            raise TypeError(f"name is expected to be None or str not {type(value)}")
        self._name = value

    @property
    def detector(self) -> NXdetector | None:
        return self._detector

    @detector.setter
    def detector(self, detector: NXdetector | None) -> None:
        if not isinstance(detector, (type(None), NXdetector)):
            raise TypeError(
                f"detector is expected to be an instance of {NXdetector} or None. Not {type(detector)}"
            )
        self._detector = detector

    @property
    def source(self) -> NXsource | None:
        return self._source

    @source.setter
    def source(self, source: NXsource | None) -> None:
        if not isinstance(source, (type(None), NXsource)):
            raise TypeError(
                f"source is expected to be an instance of {NXsource} or None. Not {type(source)}"
            )
        self._source = source

    @property
    def monochromator(self) -> NXmonochromator | None:
        return self._monochromator

    @monochromator.setter
    def monochromator(self, mono: NXmonochromator | None) -> None:
        if not isinstance(mono, (type(None), NXmonochromator)):
            raise TypeError(
                f"monochromator is expected to be an instance of {NXmonochromator} or None. Not {type(mono)}"
            )
        self._monochromator = mono

    def to_nx_dict(
        self,
        nexus_path_version: float | None = None,
        data_path: str | None = None,
    ) -> dict:
        _ = get_paths(nexus_path_version)
        nx_dict = {}

        if self.name is not None:
            nx_dict[f"{self.path}/name"] = self.name
        if self.detector is not None:
            nx_dict.update(self.detector.to_nx_dict(nexus_path_version))
        if self.source is not None:
            nx_dict.update(self.source.to_nx_dict(nexus_path_version))
        if self.monochromator is not None:
            nx_dict.update(self.monochromator.to_nx_dict(nexus_path_version))

        if nx_dict:
            nx_dict[f"{self.path}@NX_class"] = "NXinstrument"
        return nx_dict

    def _load(
        self,
        file_path: str,
        data_path: str,
        nexus_version: float,
    ) -> NXobject:
        _ = get_paths(nexus_version)
        self.name = get_data(file_path, "/".join([data_path, "name"]))
        if self.detector is not None:
            self.detector._load(
                file_path, "/".join([data_path, "detector"]), nexus_version
            )
        if self.source is not None:
            self.source._load(
                file_path, "/".join([data_path, "source"]), nexus_version
            )
        if self.monochromator is not None:
            self.monochromator._load(
                file_path, "/".join([data_path, "monochromator"]), nexus_version
            )
