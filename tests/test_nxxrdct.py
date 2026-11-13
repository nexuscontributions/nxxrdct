import re

import h5py
import numpy as np
import pint
import pytest

from nxxrdct import NXxrdct


def _build_nxxrdct():
    ureg = pint.get_application_registry()
    nx = NXxrdct()
    nx.title = "test-entry"
    nx.beam.incident_energy = 60 * ureg.keV
    nx.sample.name = "sample-1"
    nx.sample.rotation_angles = np.linspace(0, 180, 3) * ureg.degree
    nx.sample.translation_values = np.array([0.0, 1.0]) * ureg.meter
    nx.instrument.name = "id15a"
    nx.instrument.source.name = "undulator"
    nx.instrument.source.type = "synchrotron"
    nx.instrument.source.probe = "x-ray"
    nx.instrument.monochromator.wavelength = 0.184 * ureg.nanometer
    nx.instrument.detector.polar_angle = np.array([1.0, 2.0, 3.0]) * ureg.degree
    nx.instrument.detector.data = h5py.ExternalLink("raw.h5", "/entry/data")
    nx.data.radial_axis = np.linspace(1.0, 4.0, 4) * ureg.degree
    nx.data.radial_axis_long_name = "2theta"
    nx.control.mode = "monitor"
    nx.control.preset = 1.0
    nx.control.integral = 42.0
    nx.data.intensity = np.zeros((2, 3, 4))
    nx.data.intensity_errors = np.ones((2, 3, 4))
    return nx


def test_save_builds_expected_structure(tmp_path):
    nx = _build_nxxrdct()
    file_path = tmp_path / "out.nxs"
    nx.save(str(file_path), data_path="entry")

    with h5py.File(file_path, mode="r") as h5f:
        assert "entry" in h5f
        entry = h5f["entry"]
        assert entry.attrs["definition"] in ("NXxrdct", b"NXxrdct")
        assert entry.attrs["NX_class"] in ("NXentry", b"NXentry")
        assert entry.attrs["default"] in ("data", b"data")

        assert "data" in entry
        data_group = entry["data"]
        assert data_group.attrs["NX_class"] in ("NXdata", b"NXdata")
        assert data_group.attrs["signal"] in ("I", b"I")
        assert data_group.attrs["interpretation"] == "image"
        np.testing.assert_array_equal(
            data_group.attrs["axes"],
            ["translation_values", "rotation_angles", "radial_axis"],
        )
        np.testing.assert_array_equal(
            data_group.attrs["default_slice"], [".", ".", "0"]
        )
        assert isinstance(data_group.get("I", getlink=True), h5py.HardLink)
        assert data_group["I"].shape == (2, 3, 4)
        assert data_group["I"].attrs["long_name"] == "intensity"
        assert data_group["I"].attrs["units"] == "arbitrary units"
        assert data_group["radial_axis"].attrs["long_name"] == "2theta"

        assert "sample" in entry
        assert "translation_values" in entry["sample"]
        assert "rotation_angles" in entry["sample"]

        assert "instrument" in entry
        assert "detector" in entry["instrument"]
        assert "polar_angle" in entry["instrument"]["detector"]

        assert "control" in entry
        assert "mode" in entry["control"]
        assert "preset" in entry["control"]
        assert "integral" in entry["control"]


def test_save_rejects_missing_axis(tmp_path):
    nx = _build_nxxrdct()
    nx.sample.translation_values = None
    message = (
        "translation_values must be 1D with length 2, but the given shape is None."
    )
    with pytest.raises(ValueError, match=re.escape(message)):
        nx.save(str(tmp_path / "bad.nxs"), data_path="entry")


def test_save_rejects_2d_axis(tmp_path):
    nx = _build_nxxrdct()
    nx.sample.rotation_angles = np.zeros((3, 3))
    message = "rotation_angles must be 1D with length 3, but the given shape is (3, 3)."
    with pytest.raises(ValueError, match=re.escape(message)):
        nx.save(str(tmp_path / "bad.nxs"), data_path="entry")


def test_save_rejects_data_not_3d(tmp_path):
    nx = _build_nxxrdct()
    nx.data.intensity = np.zeros((3, 4))
    message = "Intensity data must be 3D, but the given shape is (3, 4)."
    with pytest.raises(ValueError, match=re.escape(message)):
        nx.save(str(tmp_path / "bad.nxs"), data_path="entry")


def test_save_rejects_missing_intensity(tmp_path):
    nx = _build_nxxrdct()
    nx.data.intensity = None
    message = "Intensity data must be 3D, but the given shape is None."
    with pytest.raises(ValueError, match=re.escape(message)):
        nx.save(str(tmp_path / "bad.nxs"), data_path="entry")


def test_save_rejects_intensity_errors_shape(tmp_path):
    nx = _build_nxxrdct()
    nx.data.intensity_errors = np.zeros((2, 3))
    message = (
        "intensity_errors must have shape (2, 3, 4), but the given shape is (2, 3)."
    )
    with pytest.raises(ValueError, match=re.escape(message)):
        nx.save(str(tmp_path / "bad.nxs"), data_path="entry")


def test_invalid_save_keeps_existing_entry(tmp_path):
    nx = _build_nxxrdct()
    file_path = str(tmp_path / "out.nxs")
    nx.save(file_path, data_path="entry")
    # make the entry invalid and try to overwrite the saved one
    nx.sample.translation_values = None
    with pytest.raises(ValueError):
        nx.save(file_path, data_path="entry", overwrite=True)
    # check the original file is still valid
    with h5py.File(file_path, mode="r") as h5f:
        np.testing.assert_array_equal(
            h5f["entry/sample/translation_values"][()], [0.0, 1.0]
        )


def test_round_trip_load(tmp_path):
    nx = _build_nxxrdct()
    file_path = tmp_path / "roundtrip.nxs"
    nx.save(str(file_path), data_path="entry")

    loaded = NXxrdct().load(str(file_path), "entry")
    assert loaded.title == "test-entry"
    assert loaded.beam.incident_energy is not None
    assert loaded.sample is not None
    assert loaded.sample.rotation_angles is not None
    assert loaded.sample.translation_values is not None
    assert loaded.instrument is not None
    assert loaded.instrument.detector is not None
    assert loaded.instrument.detector.polar_angle is not None
    assert loaded.control is not None
    assert loaded.control.mode == "monitor"
    assert loaded.data.intensity is not None
    assert loaded.data.intensity_errors is not None
    assert loaded.data.radial_axis is not None
    assert loaded.data.radial_axis_long_name == "2theta"


def test_detector_data_link_survives_save_and_load(tmp_path):
    file_path = tmp_path / "entry.nxs"
    _build_nxxrdct().save(str(file_path), data_path="entry")
    with h5py.File(file_path, "r") as h5f:
        link = h5f.get("entry/instrument/detector/data", getlink=True)
        assert isinstance(link, h5py.ExternalLink)
        assert (link.filename, link.path) == ("raw.h5", "/entry/data")

    loaded = NXxrdct().load(str(file_path), "entry")
    link = loaded.instrument.detector.data
    assert isinstance(link, h5py.ExternalLink)
    assert (link.filename, link.path) == ("raw.h5", "/entry/data")


def test_detector_data_rejects_array():
    nx = NXxrdct()
    with pytest.raises(TypeError):
        nx.instrument.detector.data = np.zeros((2, 4, 5))
