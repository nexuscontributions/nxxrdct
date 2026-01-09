"""
Base class for NXxrdct objects.
"""

from __future__ import annotations

import os

import h5py
from silx.io.dictdump import dicttonx


class NXobject:
    __isfrozen = False

    def __init__(self, node_name: str, parent=None) -> None:
        if not isinstance(node_name, str):
            raise TypeError(
                f"node_name is expected to be an instance of str. Not {type(node_name)}"
            )
        if "/" in node_name:
            raise ValueError(
                "'/' found in node_name parameter. This is a reserved character."
            )
        self.node_name = node_name
        self.parent = parent
        self._set_freeze()

    def _set_freeze(self, freeze: bool = True) -> None:
        self.__isfrozen = freeze

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent) -> None:
        if not isinstance(parent, (type(None), NXobject)):
            raise TypeError(
                f"parent is expected to be None or an instance of {NXobject}. Got {type(parent)}"
            )
        self._parent = parent

    @property
    def is_root(self) -> bool:
        return self.parent is None

    @property
    def path(self) -> str:
        if self.parent is not None:
            path = "/".join([self.parent.path, self.node_name])
        else:
            path = ""
        return path.replace("//", "/")

    @property
    def node_name(self) -> str:
        return self._node_name

    @node_name.setter
    def node_name(self, node_name: str) -> None:
        if not isinstance(node_name, str):
            raise TypeError(
                f"node_name should be an instance of str and not {type(node_name)}"
            )
        self._node_name = node_name

    def save(
        self,
        file_path: str,
        data_path: str | None = None,
        nexus_path_version: float | None = None,
        overwrite: bool = False,
    ) -> None:
        file_path = os.path.abspath(file_path)
        entry_path = data_path or self.path or self.node_name
        if entry_path.lstrip("/").rstrip("/") == "":
            raise ValueError(
                "root NXobject requires a valid data_path to be saved"
            )
        if os.path.exists(file_path):
            with h5py.File(file_path, mode="a") as h5f:
                if entry_path != "/" and entry_path in h5f:
                    if overwrite:
                        del h5f[entry_path]
                    else:
                        raise KeyError(f"{entry_path} already exists")

        nx_dict = self.to_nx_dict(
            nexus_path_version=nexus_path_version, data_path=data_path
        )
        dicttonx(
            nx_dict,
            h5file=file_path,
            h5path=data_path,
            update_mode="replace",
            mode="a",
        )

    def to_nx_dict(
        self,
        nexus_path_version: float | None = None,
        data_path: str | None = None,
    ) -> dict:
        raise NotImplementedError("Base class")

    def __setattr__(self, __name, __value):
        if self.__isfrozen and not hasattr(self, __name):
            raise AttributeError("can't set attribute", __name)
        super().__setattr__(__name, __value)

    @staticmethod
    def concatenate(nx_objects: tuple, node_name: str):
        raise NotImplementedError("Base class")
