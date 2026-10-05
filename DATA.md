# Data guide

Data and generated outputs are intentionally excluded from this repository.
The original rain-server project remains the authoritative location for the
working datasets and correction products.

The analysis scripts reference:

- CloudSat-Antarctica monthly precipitation climatology for 2007–2010;
- GPCP monthly precipitation, including versions 3.2 and 3.3;
- IMERG Version 7 monthly precipitation;
- ERA5-derived precipitation fields; and
- an Antarctic land/ocean mask used by the correction calculations.

Expected outputs include monthly correction-ratio NetCDF files, tabular ratio
summaries, and diagnostic plots. Obtain all input data from their authorized
providers and configure the path variables in the selected script. Do not add
large input data or generated products to Git.
