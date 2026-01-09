from nxxrdct.paths.nxxrdct import LATEST_VERSION, get_paths


def test_get_paths_default_version():
    paths = get_paths()
    assert paths.VERSION == LATEST_VERSION
    assert paths.NAME_PATH == "title"
    assert paths.DATA_GROUP == "data"


def test_get_paths_custom_version():
    paths = get_paths(2.5)
    assert paths.VERSION == 2.5
    assert paths.nx_sample_paths.ROTATION_ANGLE == "rotation_angle"
    assert paths.nx_detector_paths.DIFFRACTION_CHANNEL == "diffraction_channel"
