import numpy as np
import pint

from nxxrdct.nxobject.nxdetector import NXdetector
from nxxrdct.nxobject.nxinstrument import NXinstrument
from nxxrdct.nxobject.nxmonitor import NXmonitor
from nxxrdct.nxobject.nxmonochromator import NXmonochromator
from nxxrdct.nxobject.nxsample import NXsample
from nxxrdct.nxobject.nxsource import NXsource


def test_nxsample_to_nx_dict():
    ureg = pint.get_application_registry()
    sample = NXsample()
    sample.name = "s1"
    sample.rotation_angle = np.array([0.0, 90.0]) * ureg.degree
    sample.translation_values = np.array([0.0, 1.0]) * ureg.meter
    sample.x_translation = np.array([0.1, 0.2]) * ureg.meter
    nx_dict = sample.to_nx_dict()
    assert f"{sample.path}/name" in nx_dict
    assert f"{sample.path}/rotation_angle" in nx_dict
    assert f"{sample.path}/translation_values" in nx_dict
    assert f"{sample.path}/x_translation" in nx_dict


def test_nxdetector_to_nx_dict():
    ureg = pint.get_application_registry()
    detector = NXdetector()
    detector.data = np.zeros((2, 2))
    detector.polar_angle = np.array([1.0, 2.0]) * ureg.degree
    detector.distance = 0.5 * ureg.meter
    detector.diffraction_channel = np.arange(3)
    nx_dict = detector.to_nx_dict()
    assert f"{detector.path}/data" in nx_dict
    assert f"{detector.path}/polar_angle" in nx_dict
    assert f"{detector.path}/distance" in nx_dict
    assert f"{detector.path}/diffraction_channel" in nx_dict


def test_nxsource_to_nx_dict():
    source = NXsource()
    source.name = "undulator"
    source.type = "synchrotron"
    source.probe = "x-ray"
    nx_dict = source.to_nx_dict()
    assert f"{source.path}/name" in nx_dict
    assert f"{source.path}/type" in nx_dict
    assert f"{source.path}/probe" in nx_dict


def test_nxmonochromator_to_nx_dict():
    ureg = pint.get_application_registry()
    mono = NXmonochromator()
    mono.wavelength = 0.1 * ureg.nanometer
    nx_dict = mono.to_nx_dict()
    assert f"{mono.path}/wavelength" in nx_dict


def test_nxmonitor_to_nx_dict():
    monitor = NXmonitor()
    monitor.mode = "monitor"
    monitor.preset = 1.0
    monitor.integral = 2.0
    nx_dict = monitor.to_nx_dict()
    assert f"{monitor.path}/mode" in nx_dict
    assert f"{monitor.path}/preset" in nx_dict
    assert f"{monitor.path}/integral" in nx_dict


def test_nxinstrument_to_nx_dict_includes_children():
    instrument = NXinstrument()
    instrument.name = "id15a"
    instrument.source.name = "src"
    instrument.monochromator.wavelength = 0.1 * pint.get_application_registry().nanometer
    instrument.detector.data = np.zeros((1, 1))
    nx_dict = instrument.to_nx_dict()
    assert f"{instrument.path}/name" in nx_dict
    assert f"{instrument.path}@NX_class" in nx_dict
    assert f"{instrument.detector.path}@NX_class" in nx_dict
    assert f"{instrument.source.path}@NX_class" in nx_dict
    assert f"{instrument.monochromator.path}@NX_class" in nx_dict
