#%%
import gc
import os
import pandas as pd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy.io import loadmat
from datetime import date
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.cm import ScalarMappable
from matplotlib import gridspec
import matplotlib as mpl

#%%
# global variables


#%%
#%% Floating variables

mask_path = "/ra1/pubdat/mask_land_ocean/mask50km.mat"
mask = loadmat(mask_path)["mask50"][-60:, :].swapaxes(0, 1)
mask = np.flip(mask, axis=1)
mask_binary = mask < 75
new_mask = mask_binary.copy()
new_mask[:360, :] = mask_binary[360:, :].copy()
new_mask[360:, :] = mask_binary[:360, :].copy()
new_mask = np.flip(new_mask.T, axis=0)
new_mask_ = new_mask.astype(int)

cde_run_dte = str(date.today().strftime('%Y%m%d'))

#%% Define functions
def ds_swaplon(ds):
    """Swap longitude coordinates from [0,360] to [-180,180] and rename lat/lon."""
    if 'lon' in ds.coords:
        ds = ds.rename({'lon': 'longitude'})
    if 'lat' in ds.coords:
        ds = ds.rename({'lat': 'latitude'})
    ds = ds.assign_coords(longitude=(((ds.longitude + 180) % 360) - 180))
    return ds.sortby('longitude')
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# plot the correction ratios
def plot_correction_ratios(crfs_arr, vmin=None, vmax=None):
    """
    Plots the correction ratios for each month in a 3x4 grid.

    Parameters:
    crfs_arr (xarray.DataArray): Correction ratios with dimensions (month, latitude, longitude).
    """
    proj = ccrs.SouthPolarStereo()

    # Define the custom colormap
    mpl_cm = plt.cm.get_cmap("nipy_spectral", 21)
    ncolors = mpl_cm(np.linspace(0, 1, 21))[:20]
    ncolors[0] = [128 / 256, 100 / 256, 128 / 256, 1]
    ncolors[2] = ncolors[1].copy()
    ncolors[1] = [0.7, 0.1, 0.7, 1]
    newcmap = ListedColormap(ncolors)

    # Set discrete color levels
    vmin, vmax = vmin or 0, vmax or 8  # Increased vmax to address white areas in the map
    levels = np.linspace(vmin, vmax, len(ncolors))
    norm = BoundaryNorm(levels, newcmap.N)

    # Create a GridSpec for better control over the layout
    fig = plt.figure(figsize=(20, 15))
    gs = gridspec.GridSpec(3, 4, figure=fig, wspace=0.025, hspace=0.2)

    month_names = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    axes = []

    for month in range(1, 13):
        ax = fig.add_subplot(gs[month - 1], projection=proj)
        ax.set_extent([-180, 180, -90, -65], ccrs.PlateCarree())
        ax.coastlines(lw=0.25, resolution="110m", zorder=2)

        # Plot the correction ratio for the current month
        crf = crfs_arr.sel(month=month)
        crf.plot(ax=ax, transform=ccrs.PlateCarree(), 
             vmin=vmin, vmax=vmax, cmap=newcmap, norm=norm, add_colorbar=False, add_labels=False)

        ax.add_feature(cfeature.OCEAN, zorder=1, edgecolor=None, lw=0, color="silver", alpha=0.5)

        # Place month title in upper right corner of each subplot for better readability
        ax.text(0.95, 0.95, month_names[month - 1], 
                transform=ax.transAxes, 
                fontsize=16, fontweight='bold',
                ha='right', va='top',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='none'))

        # Add gridlines with improved positioning
        gl = ax.gridlines(draw_labels=True, x_inline=False, y_inline=False, 
                  linestyle='--', color='k', linewidth=0.75)
        gl.top_labels = False
        gl.right_labels = False
        gl.bottom_labels = True
        gl.left_labels = True
        gl.xlabel_style = {'fontsize': 12, 'fontweight': 'normal'}
        gl.ylabel_style = {'fontsize': 12, 'fontweight': 'normal'}
        gl.xpadding = 10
        gl.ypadding = 10

        axes.append(ax)

    # Add a dedicated axis for the colorbar (move outside the loop)
    cbar_ax = fig.add_axes([0.15, 0.05, 0.7, 0.02])  # [left, bottom, width, height]
    cbar = fig.colorbar(
        ScalarMappable(norm=norm, cmap=newcmap),
        cax=cbar_ax, orientation='horizontal', extend='max'
    )
    cbar.ax.tick_params(labelsize=16, labelrotation=0, width=1, length=5, direction='out')

    # Round colorbar tick labels to 1 decimal place
    ticks = cbar.get_ticks()
    cbar.ax.set_xticks(ticks)
    cbar.ax.set_xticklabels([f"{tick:.1f}" for tick in ticks])

    # Adjust layout
    plt.tight_layout(rect=[0, 0.1, 1, 1])  # Leave space for the colorbar

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def compute_monthly_ratios(reference, target):
    """
    Compute correction ratios for each month by dividing the reference data by the target data.

    Parameters:
    - reference: xarray.DataArray, the reference climatology data
    - target: xarray.DataArray, the target climatology data

    Returns:
    - xarray.DataArray containing the correction ratios for each month
    """
    return xr.concat(
        [
            xr.DataArray(
                reference.sel(month=month).values / target.sel(month=month).values,
                dims=["latitude", "longitude"],
                coords={
                    "latitude": target.latitude,
                    "longitude": target.longitude,
                    "month": month,
                },
            )
            for month in range(1, 13)
        ],
        dim="month",
    ).assign_coords(month=list(range(1, 13)))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

