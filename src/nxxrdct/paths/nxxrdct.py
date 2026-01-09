from __future__ import annotations

from dataclasses import dataclass

LATEST_VERSION = 1.0


@dataclass(frozen=True)
class NXxrdctPaths:
    VERSION: float
    NAME_PATH: str = "title"
    START_TIME_PATH: str = "start_time"
    END_TIME_PATH: str = "end_time"
    ENERGY_PATH: str = "beam/incident_energy"
    BEAM_PATH: str = "beam"

    SAMPLE_PATH: str = "sample"
    INSTRUMENT_PATH: str = "instrument"
    CONTROL_PATH: str = "control"

    DATA_GROUP: str = "data"

    class NXSamplePaths:
        NAME: str = "name"
        ROTATION_ANGLE: str = "rotation_angle"
        TRANSLATION_VALUES: str = "translation_values"
        X_TRANSLATION: str = "x_translation"
        Y_TRANSLATION: str = "y_translation"
        Z_TRANSLATION: str = "z_translation"

    class NXDetectorPaths:
        DATA: str = "data"
        POLAR_ANGLE: str = "polar_angle"
        COUNT_TIME: str = "count_time"
        DISTANCE: str = "distance"
        X_PIXEL_SIZE: str = "x_pixel_size"
        Y_PIXEL_SIZE: str = "y_pixel_size"
        DIFFRACTION_CHANNEL: str = "diffraction_channel"

    class NXSourcePaths:
        NAME: str = "name"
        TYPE: str = "type"
        PROBE: str = "probe"

    class NXMonitorPaths:
        DATA: str = "data"
        MODE: str = "mode"
        PRESET: str = "preset"
        INTEGRAL: str = "integral"

    class NXMonochromatorPaths:
        WAVELENGTH: str = "wavelength"

    nx_sample_paths = NXSamplePaths()
    nx_detector_paths = NXDetectorPaths()
    nx_source_paths = NXSourcePaths()
    nx_monitor_paths = NXMonitorPaths()
    nx_monochromator_paths = NXMonochromatorPaths()


def get_paths(version: float | None = None) -> NXxrdctPaths:
    if version is None:
        version = LATEST_VERSION
    return NXxrdctPaths(VERSION=version)
