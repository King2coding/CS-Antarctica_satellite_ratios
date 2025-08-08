# Antarctica GPCP Precipitation Correction

A Python package for computing correction ratios for GPCP precipitation products over Antarctica using CloudSat-Antarctica climatology data.

## Overview

This project computes correction ratios for Global Precipitation Climatology Project (GPCP) precipitation products specifically tailored for Antarctica's land regions. The correction process leverages CloudSat-Antarctica climatology data (2007-2010) to improve the accuracy of GPCP precipitation estimates over Antarctica.

## Features

- **Monthly Correction Ratios**: Generates 12 monthly correction factors as spatial maps
- **Single Value Corrections**: Provides spatially-averaged correction ratios for each month
- **Multiple Methods**: Implements both direct ratio calculation and Reza's smoothing method
- **Visualization**: Creates publication-ready plots of correction ratios
- **Antarctic Focus**: Specifically designed for Antarctic land regions using appropriate masks

## Key Outputs

1. **Spatial Correction Maps**: 12 monthly maps showing correction ratios across Antarctica
2. **Time Series**: Monthly correction factors for temporal analysis
3. **Comparison Plots**: Side-by-side comparison of different correction methods

## Methods

### Direct Method
- Computes simple ratios between CloudSat and GPCP climatologies
- Applies land mask filtering for Antarctica
- Generates monthly correction factors

### Reza's Method
- Uses quantile-based extreme value capping
- Applies Gaussian filtering for spatial smoothing
- Implements iterative zonal averaging for convergence
- Caps final correction factors within defined bounds (1/3 to 3)

## Data Requirements

- **CloudSat-Antarctica Data**: Monthly climatology (2007-2010)
- **GPCP Data**: Monthly precipitation data (2007-2010)
- **Land Mask**: 50km resolution mask for Antarctica

## Installation

```bash
git clone https://github.com/yourusername/antarctica-precipitation-correction.git
cd antarctica-precipitation-correction
pip install -r requirements.txt
```

## Usage

```python
from antarctica_precip_correction import GPCPCorrector

# Initialize corrector
corrector = GPCPCorrector(
    cs_data_path="/path/to/cloudsat/data",
    gpcp_data_path="/path/to/gpcp/data",
    mask_path="/path/to/mask/data"
)

# Compute correction ratios
correction_ratios = corrector.compute_corrections()

# Generate plots
corrector.plot_correction_ratios(correction_ratios, save_path="/path/to/plots")
```

## File Structure

```
antarctica-precipitation-correction/
├── src/
│   ├── antarctica_precip_correction/
│   │   ├── __init__.py
│   │   ├── corrector.py
│   │   ├── plotting.py
│   │   └── utils.py
├── examples/
│   ├── basic_usage.py
│   └── advanced_analysis.ipynb
├── tests/
├── data/
│   └── sample_data/
├── plots/
├── requirements.txt
├── setup.py
└── README.md
```

## Results

The correction ratios reveal seasonal patterns in GPCP precipitation biases over Antarctica:
- **Summer months** (DJF): Generally lower correction factors
- **Winter months** (JJA): Higher correction factors indicating GPCP underestimation
- **Spatial patterns**: Coastal regions show different correction needs than interior

## Citation

If you use this work, please cite:

```bibtex
@software{antarctica_gpcp_correction,
  title={Antarctica GPCP Precipitation Correction},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/antarctica-precipitation-correction}
}
```

## License

MIT License - see LICENSE file for details.

## Contact

- Author: Your Name
- Email: your.email@domain.com
- Institution: Your Institution

## Acknowledgments

- CloudSat mission for Antarctic precipitation data
- GPCP team for global precipitation climatology
- ERA5 reanalysis data contributors
