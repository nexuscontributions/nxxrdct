# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- None.

### Changed
- None.

### Deprecated
- None.

### Removed
- None.

### Fixed
- None.

### Security
- None.

## [0.1.0b0] - 2026-09-29

### Added
- `NXdetector.radial_axis_long_name` added and is required when `radial_axis` is set. It has a value of either `q` or `2theta`.
- `get_attribute` helper in `nxxrdct.utils` to read HDF5 attributes.

### Changed
- `NXdetector.diffraction_channel` is renamed `radial_axis`.
- `data/intensity` is now a soft link to `instrument/detector/data` instead of
  a second copy of the array.
- `NXsample.rotation_angle` is renamed `rotation_angles`.
- Linting and formatting now use ruff only.
- Angle `@units` are written in short form (`deg`) like the other fields.

### Deprecated
- Setting `NXxrdct.intensity`; use `instrument.detector.data`.
- Setting `NXsample.rotation_angle`; use `rotation_angles`.
- Setting `NXdetector.diffraction_channel`; use `radial_axis`.

## [0.1.0a0] - 2026-01-25

### Added
- Initial NXxrdct API with NXentry, instrument, sample, and control objects.
- NXmonochromator support with wavelength metadata.
- Detector metadata for polar angles and diffraction channels.
- Sample translation values metadata for XRD-CT axes.
- NXdata intensity handling with axis linking and signal designation.
- Paths/constants module for NXxrdct schema fields.
- HDF5 utility helpers for reading datasets and quantities.
- README quick start example for saving an NXxrdct entry.
- Comprehensive unit tests for API objects, paths, utilities, and application I/O.

[Unreleased]: https://github.com/nexuscontributions/nxxrdct/compare/v0.1.0b0...HEAD
[0.1.0b0]: https://github.com/nexuscontributions/nxxrdct/compare/v0.1.0a0...v0.1.0b0
[0.1.0a0]: https://github.com/nexuscontributions/nxxrdct/releases/tag/v0.1.0a0