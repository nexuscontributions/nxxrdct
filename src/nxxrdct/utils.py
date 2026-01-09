"""General utility helpers."""

from __future__ import annotations

import h5py
import pint
from silx.io.utils import h5py_read_dataset
from silx.io.utils import open as hdf5_open

_ureg = pint.get_application_registry()

__all__ = [
    "get_data",
    "get_quantity",
]


def get_quantity(
    file_path: str, data_path: str, default_unit: pint.Unit
) -> pint.Quantity | None:
    """
    Return the value and unit of an HDF5 dataset. If the unit is not found, fall back on `default_unit`.

    :param file_path: file path location of the HDF5 dataset to read.
    :param data_path: data path location of the HDF5 dataset to read.
    :param default_unit: default unit to use if the dataset has no ``unit`` or ``units`` attribute.
    :return: pint.Quantity with the data and associated unit, or None when missing.
    """
    with hdf5_open(file_path) as h5f:
        if data_path in h5f and isinstance(h5f[data_path], h5py.Dataset):
            dataset = h5f[data_path]
            unit = None
            if "unit" in dataset.attrs:
                unit = dataset.attrs["unit"]
            elif "units" in dataset.attrs:
                unit = dataset.attrs["units"]
            else:
                unit = str(default_unit)
            if hasattr(unit, "decode"):
                unit = unit.decode()
            unit = _ureg(str(unit))
            data = h5py_read_dataset(dataset)
            return data * unit
    return None


def get_data(file_path: str, data_path: str):
    """
    Read data from the HDF5 dataset or return None when missing.
    """
    with hdf5_open(file_path) as h5f:
        if data_path in h5f:
            return h5py_read_dataset(h5f[data_path])
    return None
