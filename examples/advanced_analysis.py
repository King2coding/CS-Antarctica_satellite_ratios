"""
Advanced analysis notebook for Antarctica GPCP Precipitation Correction.

This notebook provides detailed analysis and visualization of correction ratios,
including sensitivity analysis and validation studies.
"""

# Cell 1: Setup and imports
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xarray as xr

# Add package to path for development
sys.path.insert(0, os.path.join('..', 'src'))
from antarctica_precip_correction import GPCPCorrector, plot_correction_ratios

# Cell 2: Configuration
# Data paths - adjust these to your actual data locations
CS_DATA_PATH = "/ra1/pubdat/AVHRR_CloudSat_proj/CS_Antartica_analysis_kkk/CS-Antarctica_maps"
GPCP_DATA_PATH = "/ra1/pubdat/Satellite_eval_over_Oceans/data/GPCP/GPCP_v3_pnt_3_monthly"
MASK_PATH = "/ra1/pubdat/mask_land_ocean/mask50km.mat"
OUTPUT_PATH = "./advanced_outputs"

# Create output directory
os.makedirs(OUTPUT_PATH, exist_ok=True)

# Cell 3: Initialize corrector and load data
print("Initializing GPCP Corrector...")
corrector = GPCPCorrector(
    cs_data_path=CS_DATA_PATH,
    gpcp_data_path=GPCP_DATA_PATH,
    mask_path=MASK_PATH,
    output_path=OUTPUT_PATH
)

# Load individual datasets for analysis
mask = corrector.load_mask()
cs_data = corrector.load_cloudsat_data()
gpcp_data = corrector.load_gpcp_data()

print(f"CloudSat data shape: {cs_data.shape}")
print(f"GPCP data shape: {gpcp_data.shape}")
print(f"Mask shape: {mask.shape}")

# Cell 4: Compute correction ratios with both methods
print("Computing correction ratios...")
direct_ratios = corrector.compute_direct_ratios()
reza_ratios = corrector.compute_reza_ratios()

# Cell 5: Statistical analysis
print("Performing statistical analysis...")

# Calculate statistics for each method
direct_stats = {
    'mean': direct_ratios.mean().item(),
    'std': direct_ratios.std().item(),
    'min': direct_ratios.min().item(),
    'max': direct_ratios.max().item(),
    'median': direct_ratios.median().item()
}

reza_stats = {
    'mean': reza_ratios.mean().item(),
    'std': reza_ratios.std().item(),
    'min': reza_ratios.min().item(),
    'max': reza_ratios.max().item(),
    'median': reza_ratios.median().item()
}

print("Direct Method Statistics:")
for key, value in direct_stats.items():
    print(f"  {key.capitalize()}: {value:.3f}")

print("\nReza's Method Statistics:")
for key, value in reza_stats.items():
    print(f"  {key.capitalize()}: {value:.3f}")

# Cell 6: Monthly variability analysis
direct_monthly_stats = []
reza_monthly_stats = []

month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

for month in range(1, 13):
    direct_month = direct_ratios.sel(month=month)
    reza_month = reza_ratios.sel(month=month)
    
    direct_monthly_stats.append({
        'month': month_names[month-1],
        'mean': direct_month.mean().item(),
        'std': direct_month.std().item(),
        'spatial_coverage': (~np.isnan(direct_month)).sum().item()
    })
    
    reza_monthly_stats.append({
        'month': month_names[month-1],
        'mean': reza_month.mean().item(),
        'std': reza_month.std().item(),
        'spatial_coverage': (~np.isnan(reza_month)).sum().item()
    })

direct_monthly_df = pd.DataFrame(direct_monthly_stats)
reza_monthly_df = pd.DataFrame(reza_monthly_stats)

print("\nMonthly Statistics - Direct Method:")
print(direct_monthly_df.round(3))

print("\nMonthly Statistics - Reza's Method:")
print(reza_monthly_df.round(3))

# Cell 7: Visualization
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Monthly means comparison
axes[0,0].plot(range(1, 13), direct_monthly_df['mean'], 'o-', label='Direct Method', linewidth=2)
axes[0,0].plot(range(1, 13), reza_monthly_df['mean'], 's-', label="Reza's Method", linewidth=2)
axes[0,0].set_xlabel('Month')
axes[0,0].set_ylabel('Mean Correction Ratio')
axes[0,0].set_title('Monthly Mean Correction Ratios')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)
axes[0,0].set_xticks(range(1, 13))
axes[0,0].set_xticklabels(month_names, rotation=45)

# Monthly standard deviations
axes[0,1].plot(range(1, 13), direct_monthly_df['std'], 'o-', label='Direct Method', linewidth=2)
axes[0,1].plot(range(1, 13), reza_monthly_df['std'], 's-', label="Reza's Method", linewidth=2)
axes[0,1].set_xlabel('Month')
axes[0,1].set_ylabel('Standard Deviation')
axes[0,1].set_title('Monthly Variability')
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)
axes[0,1].set_xticks(range(1, 13))
axes[0,1].set_xticklabels(month_names, rotation=45)

# Histogram comparison for a specific month (January)
jan_direct = direct_ratios.sel(month=1).values.flatten()
jan_reza = reza_ratios.sel(month=1).values.flatten()
jan_direct = jan_direct[~np.isnan(jan_direct)]
jan_reza = jan_reza[~np.isnan(jan_reza)]

axes[1,0].hist(jan_direct, bins=50, alpha=0.7, label='Direct Method', density=True)
axes[1,0].hist(jan_reza, bins=50, alpha=0.7, label="Reza's Method", density=True)
axes[1,0].set_xlabel('Correction Ratio')
axes[1,0].set_ylabel('Density')
axes[1,0].set_title('January Correction Ratio Distribution')
axes[1,0].legend()

# Scatter plot comparison
direct_flat = direct_ratios.values.flatten()
reza_flat = reza_ratios.values.flatten()
valid_mask = ~(np.isnan(direct_flat) | np.isnan(reza_flat))
direct_flat = direct_flat[valid_mask]
reza_flat = reza_flat[valid_mask]

axes[1,1].scatter(direct_flat, reza_flat, alpha=0.5, s=1)
axes[1,1].plot([0, 8], [0, 8], 'r--', linewidth=2, label='1:1 line')
axes[1,1].set_xlabel('Direct Method')
axes[1,1].set_ylabel("Reza's Method")
axes[1,1].set_title('Method Comparison')
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_PATH, 'advanced_analysis.png'), dpi=300, bbox_inches='tight')
plt.show()

# Cell 8: Seasonal analysis
seasons = {
    'DJF': [12, 1, 2],  # Summer
    'MAM': [3, 4, 5],   # Autumn
    'JJA': [6, 7, 8],   # Winter
    'SON': [9, 10, 11]  # Spring
}

seasonal_analysis = []

for season_name, months in seasons.items():
    direct_seasonal = direct_ratios.sel(month=months).mean(dim='month')
    reza_seasonal = reza_ratios.sel(month=months).mean(dim='month')
    
    seasonal_analysis.append({
        'season': season_name,
        'direct_mean': direct_seasonal.mean().item(),
        'direct_std': direct_seasonal.std().item(),
        'reza_mean': reza_seasonal.mean().item(),
        'reza_std': reza_seasonal.std().item()
    })

seasonal_df = pd.DataFrame(seasonal_analysis)
print("\nSeasonal Analysis:")
print(seasonal_df.round(3))

# Cell 9: Save results
print("Saving results...")

# Save correction ratios
corrector.save_results(direct_ratios, "_advanced", "direct")
corrector.save_results(reza_ratios, "_advanced", "reza")

# Save analysis results
analysis_results = {
    'direct_stats': direct_stats,
    'reza_stats': reza_stats,
    'monthly_stats': {
        'direct': direct_monthly_df.to_dict('records'),
        'reza': reza_monthly_df.to_dict('records')
    },
    'seasonal_stats': seasonal_df.to_dict('records')
}

import json
with open(os.path.join(OUTPUT_PATH, 'analysis_summary.json'), 'w') as f:
    json.dump(analysis_results, f, indent=2)

print(f"Advanced analysis complete! Results saved to {OUTPUT_PATH}")

# Cell 10: Generate spatial plots with different color ranges
print("Generating spatial plots with different visualizations...")

# Plot with standard range
fig1 = plot_correction_ratios(direct_ratios, vmin=0, vmax=8, 
                             title_suffix="Direct Method (0-8 range)")
plt.savefig(os.path.join(OUTPUT_PATH, 'direct_ratios_0_8.png'), dpi=300, bbox_inches='tight')

# Plot with extended range to capture extremes
fig2 = plot_correction_ratios(direct_ratios, vmin=0, vmax=12, 
                             title_suffix="Direct Method (0-12 range)")
plt.savefig(os.path.join(OUTPUT_PATH, 'direct_ratios_0_12.png'), dpi=300, bbox_inches='tight')

# Plot Reza method
fig3 = plot_correction_ratios(reza_ratios, vmin=0, vmax=8, 
                             title_suffix="Reza's Method")
plt.savefig(os.path.join(OUTPUT_PATH, 'reza_ratios_0_8.png'), dpi=300, bbox_inches='tight')

plt.show()

print("Advanced analysis notebook complete!")
