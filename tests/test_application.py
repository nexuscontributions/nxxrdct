import h5py
import numpy as np
import pint

from nxxrdct.application.nxxrdct import NXxrdct, copy_nxxrdct_file


def _build_entry():
    ureg = pint.get_application_registry()
    nx = NXxrdct()
    nx.title = "entry"
    nx.energy = 30 * ureg.keV
    nx.sample.name = "sample"
    nx.sample.rotation_angle = np.array([0.0, 90.0]) * ureg.degree
    nx.sample.translation_values = np.array([0.0, 1.0]) * ureg.meter
    nx.instrument.name = "id15a"
    nx.instrument.source.name = "src"
    nx.instrument.source.type = "synchrotron"
    nx.instrument.source.probe = "x-ray"
    nx.instrument.monochromator.wavelength = 0.1 * ureg.nanometer
    nx.instrument.detector.polar_angle = np.array([1.0, 2.0]) * ureg.degree
    nx.instrument.detector.diffraction_channel = np.arange(2)
    nx.control.mode = "monitor"
    nx.control.preset = 1.0
    nx.control.integral = 2.0
    nx.intensity = np.zeros((2, 2, 2))
    return nx


def test_save_and_load_roundtrip(tmp_path):
    nx = _build_entry()
    file_path = tmp_path / "entry.nxs"
    nx.save(str(file_path), data_path="entry")

    loaded = NXxrdct().load(str(file_path), "entry")
    assert loaded.title == "entry"
    assert loaded.energy is not None
    assert loaded.sample.name == "sample"
    assert loaded.sample.rotation_angle is not None
    assert loaded.sample.translation_values is not None
    assert loaded.instrument.name == "id15a"
    assert loaded.instrument.monochromator.wavelength is not None
    assert loaded.instrument.detector.polar_angle is not None
    assert loaded.instrument.detector.diffraction_channel is not None
    assert loaded.control.mode == "monitor"
    assert loaded.intensity is not None


def test_get_valid_entries_and_copy(tmp_path):
    file_path = tmp_path / "multi.nxs"
    _build_entry().save(str(file_path), data_path="entry1")
    _build_entry().save(str(file_path), data_path="entry2", overwrite=True)

    entries = NXxrdct.get_valid_entries(str(file_path))
    assert "/entry1" in entries
    assert "/entry2" in entries

    out_path = tmp_path / "copy.nxs"
    copy_nxxrdct_file(
        input_file=str(file_path),
        output_file=str(out_path),
        entries=("/entry1",),
    )

    with h5py.File(out_path, mode="r") as h5f:
        assert "entry1" in h5f
        assert "entry2" not in h5f


def test_copy_all_entries_when_none(tmp_path):
    file_path = tmp_path / "multi_all.nxs"
    _build_entry().save(str(file_path), data_path="entry1")
    _build_entry().save(str(file_path), data_path="entry2", overwrite=True)

    out_path = tmp_path / "all_copy.nxs"
    copy_nxxrdct_file(
        input_file=str(file_path),
        output_file=str(out_path),
        entries=None,
    )

    with h5py.File(out_path, mode="r") as h5f:
        assert "entry1" in h5f
        assert "entry2" in h5f


def test_node_is_nxxrdct_definition(tmp_path):
    file_path = tmp_path / "def.nxs"
    with h5py.File(file_path, mode="w") as h5f:
        entry = h5f.create_group("entry")
        entry.attrs["definition"] = "NXxrdct"
        entry.attrs["NX_class"] = "NXentry"

    with h5py.File(file_path, mode="r") as h5f:
        assert NXxrdct.node_is_nxxrdct(h5f["entry"])


def test_node_is_nxxrdct_instrument_detector(tmp_path):
    file_path = tmp_path / "instrument.nxs"
    with h5py.File(file_path, mode="w") as h5f:
        entry = h5f.create_group("entry")
        entry.attrs["NX_class"] = "NXentry"
        instrument = entry.create_group("instrument")
        instrument.attrs["NX_class"] = "NXinstrument"
        instrument.create_group("detector")

    with h5py.File(file_path, mode="r") as h5f:
        assert NXxrdct.node_is_nxxrdct(h5f["entry"])
