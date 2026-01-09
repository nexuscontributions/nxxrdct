"""Define NXxrdct application and related functions and classes."""

from __future__ import annotations

import logging
import os
from datetime import datetime

import h5py
import pint
from silx.io.utils import open as hdf5_open

from nxxrdct.nxobject.nxdetector import NXdetector
from nxxrdct.nxobject.nxinstrument import NXinstrument
from nxxrdct.nxobject.nxmonitor import NXmonitor
from nxxrdct.nxobject.nxobject import NXobject
from nxxrdct.nxobject.nxsample import NXsample
from nxxrdct.paths.nxxrdct import LATEST_VERSION, get_paths
from nxxrdct.utils import get_data, get_quantity

_ureg = pint.get_application_registry()

_logger = logging.getLogger(__name__)

__all__ = ["NXxrdct", "copy_nxxrdct_file"]


class NXxrdct(NXobject):
    """
    Class defining an NXxrdct entry.
    """

    def __init__(self, parent: NXobject | None = None) -> None:
        super().__init__(node_name="", parent=parent)
        self._set_freeze(False)
        self._start_time = None
        self._end_time = None
        self._title = None
        self._energy = None
        self._intensity = None
        self._instrument = NXinstrument(node_name="instrument", parent=self)
        self._sample = NXsample(node_name="sample", parent=self)
        self._control = NXmonitor(node_name="control", parent=self)
        self._set_freeze(True)

    @property
    def start_time(self) -> datetime | str | None:
        return self._start_time

    @start_time.setter
    def start_time(self, value: datetime | str | None):
        if not isinstance(value, (type(None), datetime, str)):
            raise TypeError(
                f"start_time is expected to be datetime, str, or None. Not {type(value)}"
            )
        self._start_time = value

    @property
    def end_time(self) -> datetime | str | None:
        return self._end_time

    @end_time.setter
    def end_time(self, value: datetime | str | None):
        if not isinstance(value, (type(None), datetime, str)):
            raise TypeError(
                f"end_time is expected to be datetime, str, or None. Not {type(value)}"
            )
        self._end_time = value

    @property
    def title(self) -> str | None:
        return self._title

    @title.setter
    def title(self, value: str | None):
        if not isinstance(value, (type(None), str)):
            raise TypeError(f"title is expected to be str or None. Not {type(value)}")
        self._title = value

    @property
    def energy(self) -> pint.Quantity | None:
        return self._energy

    @energy.setter
    def energy(self, value: pint.Quantity | None):
        if value is None:
            self._energy = None
        elif isinstance(value, pint.Quantity):
            self._energy = value.to(_ureg.keV)
        else:
            self._energy = _ureg.Quantity(value, _ureg.keV)

    @property
    def intensity(self):
        return self._intensity

    @intensity.setter
    def intensity(self, value):
        self._intensity = value

    @property
    def instrument(self) -> NXinstrument | None:
        return self._instrument

    @instrument.setter
    def instrument(self, value: NXinstrument | None) -> None:
        if not isinstance(value, (type(None), NXinstrument)):
            raise TypeError(
                f"instrument is expected to be {NXinstrument} or None. Not {type(value)}"
            )
        self._instrument = value

    @property
    def sample(self) -> NXsample | None:
        return self._sample

    @sample.setter
    def sample(self, value: NXsample | None) -> None:
        if not isinstance(value, (type(None), NXsample)):
            raise TypeError(
                f"sample is expected to be {NXsample} or None. Not {type(value)}"
            )
        self._sample = value

    @property
    def control(self) -> NXmonitor | None:
        return self._control

    @control.setter
    def control(self, value: NXmonitor | None) -> None:
        if not isinstance(value, (type(None), NXmonitor)):
            raise TypeError(
                f"control is expected to be {NXmonitor} or None. Not {type(value)}"
            )
        self._control = value

    def to_nx_dict(
        self,
        nexus_path_version: float | None = None,
        data_path: str | None = None,
    ) -> dict:
        if data_path is None:
            data_path = ""

        nexus_paths = get_paths(nexus_path_version)
        nx_dict = {}

        if self.sample is not None:
            nx_dict.update(self.sample.to_nx_dict(nexus_path_version))
        else:
            _logger.info("no sample found. Won't be saved")

        if self.instrument is not None:
            nx_dict.update(self.instrument.to_nx_dict(nexus_path_version))
        else:
            _logger.info("no instrument found. Won't be saved")

        if self.control is not None:
            nx_dict.update(self.control.to_nx_dict(nexus_path_version))
        else:
            _logger.info("no control found. Won't be saved")

        if self.start_time is not None:
            path = f"{self.path}/{nexus_paths.START_TIME_PATH}"
            start_time = (
                self.start_time.isoformat()
                if isinstance(self.start_time, datetime)
                else self.start_time
            )
            nx_dict[path] = start_time
        if self.end_time is not None:
            path = f"{self.path}/{nexus_paths.END_TIME_PATH}"
            end_time = (
                self.end_time.isoformat()
                if isinstance(self.end_time, datetime)
                else self.end_time
            )
            nx_dict[path] = end_time
        if self.energy is not None:
            path_energy = f"{self.path}/{nexus_paths.ENERGY_PATH}"
            nx_dict[path_energy] = self.energy.magnitude
            nx_dict[f"{path_energy}@units"] = f"{self.energy.units:~}"
            path_beam = f"{self.path}/{nexus_paths.BEAM_PATH}"
            nx_dict[f"{path_beam}@NX_class"] = "NXbeam"
        if self.title is not None:
            path_title = f"{self.path}/{nexus_paths.NAME_PATH}"
            nx_dict[path_title] = self.title

        if self.intensity is not None:
            data_path_group = f"{self.path}/{nexus_paths.DATA_GROUP}"
            nx_dict[f"{data_path_group}/intensity"] = self.intensity
            nx_dict[f"{data_path_group}/intensity@signal"] = 1
            nx_dict[f"{data_path_group}@NX_class"] = "NXdata"
            nx_dict[f"{data_path_group}@signal"] = "intensity"
            nx_dict[f"{self.path}@default"] = nexus_paths.DATA_GROUP

            axes = []
            if self.sample is not None and self.sample.translation_values is not None:
                translation_path = (
                    f"/{data_path}/{self.sample.path}/translation_values"
                ).replace("//", "/")
                nx_dict[f">/{data_path_group}/translation_values"] = translation_path
                axes.append("translation_values")
            if self.sample is not None and self.sample.rotation_angle is not None:
                rotation_path = (
                    f"/{data_path}/{self.sample.path}/rotation_angle"
                ).replace("//", "/")
                nx_dict[f">/{data_path_group}/rotation_angles"] = rotation_path
                axes.append("rotation_angles")
            if (
                self.instrument is not None
                and self.instrument.detector is not None
                and self.instrument.detector.diffraction_channel is not None
            ):
                channel_path = (
                    f"/{data_path}/{self.instrument.detector.path}/diffraction_channel"
                ).replace("//", "/")
                nx_dict[f">/{data_path_group}/diffraction_channel"] = channel_path
                axes.append("diffraction_channel")
            if axes:
                nx_dict[f"{data_path_group}@axes"] = ":".join(axes)

        if nx_dict:
            nx_dict[f"{self.path}@NX_class"] = "NXentry"
            nx_dict[f"{self.path}@definition"] = "NXxrdct"
            nx_dict[f"{self.path}/definition"] = "NXxrdct"
            nx_dict[f"{self.path}@version"] = nexus_paths.VERSION

        return nx_dict

    def load(self, file_path: str, data_path: str) -> NXobject:
        if not os.path.exists(file_path):
            raise IOError(f"{file_path} does not exist")
        with hdf5_open(file_path) as h5f:
            if data_path not in h5f:
                raise ValueError(f"{data_path} cannot be found in {file_path}")
            root_node = h5f[data_path]
            if "version" in root_node.attrs:
                nexus_version = root_node.attrs["version"]
            else:
                _logger.warning(
                    f"Unable to find nexus version associated with {data_path}@{file_path}"
                )
                nexus_version = LATEST_VERSION

        nexus_paths = get_paths(nexus_version)
        self.energy = get_quantity(
            file_path=file_path,
            data_path="/".join([data_path, nexus_paths.ENERGY_PATH]),
            default_unit=_ureg.keV,
        )
        start_time = get_data(
            file_path=file_path,
            data_path="/".join([data_path, nexus_paths.START_TIME_PATH]),
        )
        try:
            start_time = datetime.fromisoformat(start_time)
        except Exception:
            start_time = str(start_time) if start_time is not None else None
        self.start_time = start_time

        end_time = get_data(
            file_path=file_path,
            data_path="/".join([data_path, nexus_paths.END_TIME_PATH]),
        )
        try:
            end_time = datetime.fromisoformat(end_time)
        except Exception:
            end_time = str(end_time) if end_time is not None else None
        self.end_time = end_time

        self.title = get_data(
            file_path=file_path, data_path="/".join([data_path, nexus_paths.NAME_PATH])
        )

        if self.sample is not None:
            self.sample._load(
                file_path, "/".join([data_path, "sample"]), nexus_version=nexus_version
            )
        if self.instrument is not None:
            self.instrument._load(
                file_path,
                "/".join([data_path, "instrument"]),
                nexus_version=nexus_version,
            )
        if self.control is not None:
            self.control._load(
                file_path, "/".join([data_path, "control"]), nexus_version=nexus_version
            )
        self.intensity = get_data(
            file_path,
            "/".join([data_path, nexus_paths.DATA_GROUP, "intensity"]),
        )
        return self

    def save(
        self,
        file_path: str,
        data_path: str,
        nexus_path_version: float | None = None,
        overwrite: bool = False,
    ) -> None:
        super().save(
            file_path=file_path,
            data_path=data_path,
            nexus_path_version=nexus_path_version,
            overwrite=overwrite,
        )

    @staticmethod
    def get_valid_entries(file_path: str) -> tuple:
        if not os.path.isfile(file_path):
            raise ValueError("given file path should be a file")

        def browse_group(group):
            res_buf = []
            for entry_alias in group.keys():
                entry = group.get(entry_alias)
                if isinstance(entry, h5py.Group):
                    if NXxrdct.node_is_nxxrdct(entry):
                        res_buf.append(entry.name)
                    else:
                        res_buf.extend(browse_group(entry))
            return res_buf

        with hdf5_open(file_path) as h5f:
            res = browse_group(h5f)
        res.sort()
        return tuple(res)

    @staticmethod
    def node_is_nxxrdct(node: h5py.Group) -> bool:
        if "definition" in node.attrs and str(node.attrs["definition"]).lower() == "nxxrdct":
            return True
        if "NX_class" not in node.attrs and "NXclass" not in node.attrs:
            return False
        if "instrument" in node:
            instrument = node["instrument"]
            if "NX_class" in instrument.attrs and instrument.attrs["NX_class"] in (
                "NXinstrument",
                b"NXinstrument",
            ):
                return "detector" in instrument
        return False


def copy_nxxrdct_file(
    input_file: str,
    output_file: str,
    entries: tuple | None,
    overwrite: bool = False,
):
    input_file = os.path.abspath(input_file)
    output_file = os.path.abspath(output_file)
    if input_file == output_file:
        raise ValueError("input file and output file are the same")

    if entries is None:
        entries = NXxrdct.get_valid_entries(file_path=input_file)
        if len(entries) == 0:
            _logger.warning(f"no valid entries for {input_file}")

    for entry in entries:
        nx_xrdct = NXxrdct().load(input_file, entry)
        nx_xrdct.save(output_file, entry, overwrite=overwrite)
