<p align="left">
  <img src="nxxrdct/resources/nxxrdct.png" alt="nxxrdct" width="180">
</p>

The goal of the `nxxrdct` project is to provide a python API to create, load, edit, and save [NXxrdct](https://manual.nexusformat.org/classes/applications/nxxrdct.html) application definition files.


Please find at https://tomotools.gitlab-pages.esrf.fr/nxxrdct the latest documentation

```bash
pip install nxxrdct
```

Add the optional extras when you need documentation or development tooling:

```bash
pip install nxxrdct[doc,test]
```

## Quick Start
```python
import numpy as np
import pint

from nxxrdct import NXxrdct

ureg = pint.get_application_registry()

nx = NXxrdct()
nx.title = "Demo XRD-CT"
nx.beam.incident_energy = 60 * ureg.keV
nx.sample.name = "sample-01"
nx.sample.rotation_angle = np.linspace(0, 180, 181) * ureg.degree
nx.instrument.detector.data = np.zeros((181, 256, 256))
nx.instrument.detector.count_time = 0.1 * ureg.second

nx.save("demo_xrdct.h5", data_path="entry")
```

## Documentation and Support
- Latest documentation: https://nxxrdct.readthedocs.io/en/stable/index.html
- API reference: https://nxxrdct.readthedocs.io/en/stable/api.html
- Report issues and follow development on GitLab: https://github.com/nexuscontributions/nxxrdct

## Contributing
Contributions and feedback are welcome. Please open an issue or submit a merge request on GitLab. See the development guide in `doc/development` for details on setting up a local environment and running the test suite.

## License
`nxxrdct` is released under the MIT License. See `LICENSE` for the full text.
