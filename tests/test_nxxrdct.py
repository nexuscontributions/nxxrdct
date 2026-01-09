import numpy as np
import pint
import h5py

from nxxrdct import NXxrdct


def _build_nxxrdct():
    ureg = pint.get_application_registry()
    nx = NXxrdct()
    nx.title = "test-entry"
    nx.energy = 60 * ureg.keV
    nx.sample.name = "sample-1"
    nx.sample.rotation_angle = np.linspace(0, 180, 3) * ureg.degree
    nx.sample.translation_values = np.array([0.0, 1.0, 2.0]) * ureg.meter
    nx.instrument.name = "id15a"
    nx.instrument.source.name = "undulator"
    nx.instrument.source.type = "synchrotron"
    nx.instrument.source.probe = "x-ray"
    nx.instrument.monochromator.wavelength = 0.184 * ureg.nanometer
    nx.instrument.detector.polar_angle = np.array([1.0, 2.0, 3.0]) * ureg.degree
    nx.instrument.detector.diffraction_channel = np.arange(4)
    nx.control.mode = "monitor"
    nx.control.preset = 1.0
    nx.control.integral = 42.0
    nx.intensity = np.zeros((3, 3, 4))
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
        assert data_group.attrs["signal"] in ("intensity", b"intensity")
        assert data_group.attrs["axes"] in (
            "translation_values:rotation_angles:diffraction_channel",
            b"translation_values:rotation_angles:diffraction_channel",
        )
        assert "intensity" in data_group

        assert "sample" in entry
        assert "translation_values" in entry["sample"]
        assert "rotation_angle" in entry["sample"]

        assert "instrument" in entry
        assert "detector" in entry["instrument"]
        assert "polar_angle" in entry["instrument"]["detector"]
        assert "diffraction_channel" in entry["instrument"]["detector"]

        assert "control" in entry
        assert "mode" in entry["control"]
        assert "preset" in entry["control"]
        assert "integral" in entry["control"]


def test_round_trip_load(tmp_path):
    nx = _build_nxxrdct()
    file_path = tmp_path / "roundtrip.nxs"
    nx.save(str(file_path), data_path="entry")

    loaded = NXxrdct().load(str(file_path), "entry")
    assert loaded.title == "test-entry"
    assert loaded.energy is not None
    assert loaded.sample is not None
    assert loaded.sample.rotation_angle is not None
    assert loaded.sample.translation_values is not None
    assert loaded.instrument is not None
    assert loaded.instrument.detector is not None
    assert loaded.instrument.detector.polar_angle is not None
    assert loaded.instrument.detector.diffraction_channel is not None
    assert loaded.control is not None
    assert loaded.control.mode == "monitor"
    assert loaded.intensity is not None
