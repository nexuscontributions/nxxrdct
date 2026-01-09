import h5py
import pint

from nxxrdct.utils import get_data, get_quantity


def test_get_data_and_quantity(tmp_path):
    ureg = pint.get_application_registry()
    file_path = tmp_path / "data.h5"
    with h5py.File(file_path, mode="w") as h5f:
        ds = h5f.create_dataset("energy", data=12.5)
        ds.attrs["units"] = "keV"
        h5f.create_dataset("plain", data=[1, 2, 3])

    quantity = get_quantity(
        file_path=str(file_path),
        data_path="/energy",
        default_unit=ureg.keV,
    )
    assert quantity.magnitude == 12.5
    assert quantity.units == ureg.keV

    plain = get_data(file_path=str(file_path), data_path="/plain")
    assert plain.tolist() == [1, 2, 3]

    assert get_data(file_path=str(file_path), data_path="/missing") is None
    assert (
        get_quantity(
            file_path=str(file_path),
            data_path="/missing",
            default_unit=ureg.keV,
        )
        is None
    )
