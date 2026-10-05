# CloudSat-based Antarctic precipitation correction ratios

Research code for calculating monthly precipitation correction ratios over
Antarctica using the CloudSat-Antarctica 2007–2010 climatology as a reference.
The current workflows compare that climatology with GPCP versions 3.2 and 3.3,
IMERG Version 7, and ERA5-derived precipitation fields.

## Repository status

This repository preserves both the original analysis scripts and a later Python
package scaffold. The source has not been refactored or consolidated during the
documentation pass. The standalone research scripts remain the clearest record
of the working analysis, while the package-style interface should be treated as
an experimental organization layer.

No input datasets or generated correction maps are distributed here. The
tracked notebook is retained as part of the original code archive.

## Main analysis files

- `cs_ant_gpcp_ratios.py` calculates CloudSat-based monthly correction ratios
  for GPCP versions 3.2 and 3.3.
- `cs_ant_satellite_cor_ratios.py` extends the comparison to IMERG Version 7
  and related satellite/reanalysis processing.
- `utils.py` contains the original preprocessing, masking, correction-factor,
  smoothing, weighting, and plotting utilities.
- `src/antarctica_precip_correction/` contains the package-style corrector,
  plotting, and utility modules.
- `examples/` contains package-usage examples.
- `Interactive-1.ipynb` is an archived interactive analysis notebook.

## Method summary

The scripts:

1. load the CloudSat-Antarctica monthly climatology for 2007–2010;
2. calculate corresponding monthly climatologies from comparison products;
3. apply an Antarctic land mask and align the spatial grids;
4. calculate spatially varying monthly correction ratios;
5. apply the correction-factor processing implemented in `utils.py`; and
6. write NetCDF ratio maps, tabular summaries, and diagnostic figures to
   external output directories.

The repository documents the implemented analysis; it does not independently
validate the scientific performance of the resulting correction factors.

## Data requirements

The workflows use externally stored CloudSat-Antarctica climatology, GPCP,
IMERG, ERA5, and Antarctic mask data. Several scripts retain absolute paths
from the original rain-server environment. See [`DATA.md`](DATA.md) for details.

## Installation and execution

The recorded Python dependencies are listed in `requirements.txt`. A typical
environment can be prepared with:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Before running a script, update its input and output path variables for your
authorized local datasets. The original scripts are research workflows rather
than command-line applications and may require substantial memory for multi-file
`xarray` operations.

The existing `setup.py` is preserved byte-for-byte as part of the archive and
still contains template metadata. It should not be used as authoritative author,
repository, or command-line-interface documentation.

## Citation

Repository-level citation metadata is provided in [`CITATION.cff`](CITATION.cff).
No associated journal or manuscript citation has been assigned because the
relationship to a specific publication has not yet been independently verified.

## License status

The repository contains an existing MIT license file with template authorship
text. That file is preserved from the original history; its authorship and reuse
status should be confirmed before relying on it.

## Contact

Kwabena Kingsley Kumah — [GitHub profile](https://github.com/King2coding)
