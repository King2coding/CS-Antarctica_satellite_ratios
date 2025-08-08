#%%
'''
This script is designed to compute correction ratios for GPCP precipitation products, specifically tailored for Antarctica's land regions. 
The correction process leverages CloudSat-Antarctica climatology data (2007-2010) augmented with ERA5 data. 
The output includes 12 monthly correction ratios or factors represented as array maps, as well as single ratio values. 
These correction ratios can be applied to adjust GPCP precipitation products for improved accuracy over Antarctica.
'''

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

#%% Define the path to the input data
cs_ant_month_clim_path = r'/ra1/pubdat/AVHRR_CloudSat_proj/CS_Antartica_analysis_kkk/CS-Antarctica_maps'
gpcp_data_path = r'/ra1/pubdat/Satellite_eval_over_Oceans/data/GPCP/GPCP_v3_pnt_3_monthly'

path_to_put_plots = r'/home/kkumah/Projects/CS-Antarctica_satellite_ratios/GPCP_ratios/plots'


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

        # Place the title on the left without "month = number"
        ax.set_title(
            month_names[month - 1], 
            loc='left', fontsize=16, fontweight='bold'
        )

        # Add gridlines
        gl = ax.gridlines(draw_labels=True, x_inline=False, y_inline=False, 
                  linestyle='--', color='k', linewidth=0.75)
        gl.top_labels = False
        gl.right_labels = False
        gl.xlabel_style = {'fontsize': 16, 'fontweight': 'bold'}
        gl.ylabel_style = {'fontsize': 16, 'fontweight': 'bold'}

        axes.append(ax)

        # Add a dedicated axis for the colorbar
        cbar_ax = fig.add_axes([0.15, 0.05, 0.7, 0.02])  # [left, bottom, width, height]
        cbar = fig.colorbar(
        ScalarMappable(norm=norm, cmap=newcmap),
        cax=cbar_ax, orientation='horizontal', extend='max'
        )
        cbar.ax.tick_params(labelsize=18, labelrotation=0, width=1, length=5, direction='out')

        # Round colorbar tick labels to 1 decimal place
        ticks = cbar.get_ticks()
        cbar.ax.set_xticks(ticks)
        cbar.ax.set_xticklabels([f"{tick:.1f}" for tick in ticks])

        # Adjust layout
        plt.tight_layout(rect=[0, 0.1, 1, 1])  # Leave space for the colorbar

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


#%% Load the data
gpcp_files_2007_2010 = [
    os.path.join(gpcp_data_path, f) 
    for f in os.listdir(gpcp_data_path) 
    if f.startswith('GPCPMON_L3') and f.split('_')[2][:4] in ['2007', '2008', '2009', '2010'] \
    and f.endswith('.nc4')
]

gpcp_data = xr.open_mfdataset(gpcp_files_2007_2010, combine='by_coords', engine='netcdf4')
gpcp_data = ds_swaplon(gpcp_data)

cs_ant_mnth_clim_filenme = os.path.join(cs_ant_month_clim_path, 'CS-Antarctica_monthly_climatology_2007-2010.nc') 
cs_ant_month_clim = xr.open_dataarray(cs_ant_mnth_clim_filenme, engine='netcdf4')
cs_ant_month_clim = cs_ant_month_clim.where(new_mask_ == 1)

#%%
# Calculate monthly climatology from GPCP data
gpcp_monthly_clim = gpcp_data['sat_gauge_precip'].groupby('time.month').mean(dim='time').compute()

# Subset the data over Antarctica
gpcp_ant_monthly_clim = gpcp_monthly_clim.isel(latitude=slice(-60, None)).where(new_mask_ == 1)


#%% Calculate correction ratios
# Compute correction ratios for each month pair
# Perform the division lazily using Dask
# Ensure the dimensions align correctly before division
cs_ant_month_clim_aligned = cs_ant_month_clim.rename({'time': 'month'})

# Ensure latitude and longitude dimensions match
cs_ant_month_clim_aligned = cs_ant_month_clim_aligned.interp(
    lat=gpcp_ant_monthly_clim.latitude, 
    lon=gpcp_ant_monthly_clim.longitude
)

# Initialize an empty dictionary to store results
monthly_ratios = {}

# Loop through each month and compute the ratio
for month in range(1, 13):
    gpcp_month = gpcp_ant_monthly_clim.sel(month=month)
    cs_ant_month = cs_ant_month_clim_aligned.sel(month=month)
    monthly_ratios[month] = cs_ant_month / gpcp_month

# Convert the dictionary back to an xarray DataArray
crfs_arr = xr.concat([monthly_ratios[m] for m in range(1, 13)], dim='month')
crfs_arr = crfs_arr.assign_coords(month=list(range(1, 13)))


svnme = os.path.join(path_to_put_plots, f'GPCP_ratios_{cde_run_dte}.png')
plot_correction_ratios(crfs_arr)
plt.savefig(svnme, dpi=300)
gc.collect()


plot_correction_ratios(cs_ant_month_clim_aligned, vmin=0, vmax=1.5)

plot_correction_ratios(gpcp_ant_monthly_clim, vmin=0, vmax=1.5)

# %% calculate single value correction ratios
# Calculate single value correction ratios and store them in a DataFrame

crfs_arr_single_ = [
    {
        'month': month,
        'crf': crfs_arr.sel(month=month).mean(dim=['latitude', 'longitude'], skipna=True).item()
    }
    for month in range(1, 13)
]
# Convert the list of dictionaries to a DataFrame
crfs_arr_single_ = pd.DataFrame(crfs_arr_single_)


crfs_arr_single = [
    {
        'month': month,
        'crf': (cs_ant_month_clim_aligned.sel(month=month).mean().item() /
                gpcp_ant_monthly_clim.sel(month=month).mean().item())
    }
    for month in range(1, 13)
]

# Convert the list of dictionaries to a DataFrame
crfs_arr_single = pd.DataFrame(crfs_arr_single)

# make a bar plot of the single value correction ratios
# Update matplotlib parameters for improved aesthetics
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.serif'] = ['Times New Roman']
mpl.rcParams['font.weight'] = 'bold'
mpl.rcParams['axes.labelweight'] = 'bold'
mpl.rcParams['axes.titleweight'] = 'bold'
mpl.rcParams['xtick.labelsize'] = 18
mpl.rcParams['ytick.labelsize'] = 18
mpl.rcParams['axes.titlesize'] = 18
mpl.rcParams['axes.labelsize'] = 18

# Create the bar plot with updated styles
plt.figure(figsize=(10, 6))
plt.bar(crfs_arr_single['month'], crfs_arr_single['crf'], color='skyblue')
plt.xticks(crfs_arr_single['month'], 
           ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 
           fontsize=18, fontweight='bold', family='Times New Roman')
plt.xlabel('Month', fontsize=18, fontweight='bold', family='Times New Roman')
plt.ylabel('Correction Ratio', fontsize=18, fontweight='bold', family='Times New Roman')
plt.title('Monthly Correction Ratios for GPCP Precipitation Products', fontsize=18, fontweight='bold', family='Times New Roman')
plt.grid(axis='y')
plt.tight_layout()

# Save the plot
plt.savefig(os.path.join(path_to_put_plots, f'GPCP_ratios_single_{cde_run_dte}.png'), dpi=300)
plt.show()


#%% Reza method
from scipy.ndimage import gaussian_filter
from scipy.signal import convolve2d

def cf_calculator(reference, target, mask, quantile=1 - 1e-6):
    product_land = np.where(mask, target, np.nan)
    q99 = np.nanquantile(product_land, quantile)
    new_product = np.where(product_land > q99, q99, target)
    new_product = np.where(~mask, target, new_product)
    product_smoothed = apply_filter(new_product)

    return reference / product_smoothed

def apply_filter(
    array, method="convolution", sigma=1.4, kernel=np.ones((5, 5))
):
    if method == "gaussian":
        new_array = gaussian_filter(array, sigma=(sigma, sigma), order=0)
    elif method == "convolution":
        new_array = convolve2d(array, kernel, boundary="symm", mode="same")
        new_array = new_array / kernel.sum()

    return new_array

CAP = 3


def apply_cap(array, minimum=1 / CAP, maximum=CAP):
    temp = np.where(array > maximum, maximum, array)
    temp = np.where(temp < minimum, minimum, temp)

    return temp


def get_zonal(spatial_product, mask, y, axis=(0, 1)):
    cosines = np.cos(np.radians(y))[:, np.newaxis]  # Broadcast to match mask shape
    cosines = np.where(mask, cosines, 0)
    weights = cosines / np.nansum(cosines)

    return np.nansum(weights * spatial_product, axis=axis)


def cf_smoother(reference, target, cf, mask, y):
    # cf_smoothed = apply_filter(cf)
    cf_capped = apply_cap(cf)
    zonal_reference = get_zonal(reference, mask, y)
    zonal_product = get_zonal(target * cf_capped, mask, y)
    ratio = zonal_reference / zonal_product
    i = 1
    while (abs(1 - ratio) > 1e-3) and (i < 5):
        apply_conditional = (cf_capped <= CAP) & (cf_capped >= 1 / CAP)
        cf_capped = np.where(apply_conditional, cf_capped * ratio, cf_capped)
        zonal_product = get_zonal(target * cf_capped, mask, y)
        ratio = zonal_reference / zonal_product
        i += 1

    return cf_capped

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Calculate correction factors using the Reza method
crfs_arr_reza = xr.concat(
    [
        xr.DataArray(
            cf_calculator(
                cs_ant_month_clim_aligned.sel(month=month).values,
                gpcp_ant_monthly_clim.sel(month=month).values,
                new_mask_,
            ),
            dims=["latitude", "longitude"],
            coords={
                "latitude": gpcp_ant_monthly_clim.latitude,
                "longitude": gpcp_ant_monthly_clim.longitude,
                "month": month,
            },
        )
        for month in range(1, 13)
    ],
    dim="month",
)
crfs_arr_reza = crfs_arr_reza.assign_coords(month=list(range(1, 13)))

# apply the smoothing and zonal averaging
crfs_arr_reza_smoothed = xr.concat(
    [
        xr.DataArray(
            cf_smoother(
                cs_ant_month_clim_aligned.sel(month=month).values,
                gpcp_ant_monthly_clim.sel(month=month).values,
                crfs_arr_reza.sel(month=month).values,
                new_mask_,
                gpcp_ant_monthly_clim.latitude.values,
            ),
            dims=["latitude", "longitude"],
            coords={
                "latitude": gpcp_ant_monthly_clim.latitude,
                "longitude": gpcp_ant_monthly_clim.longitude,    
                "month": month,
            },
        )
        for month in range(1, 13)
    ],
    dim="month",
)
crfs_arr_reza_smoothed = crfs_arr_reza_smoothed.assign_coords(month=list(range(1, 13)))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# do some plotting
svnme_reza = os.path.join(path_to_put_plots, f'GPCP_ratios_reza_{cde_run_dte}.png')
plot_correction_ratios(crfs_arr_reza_smoothed, vmin=0, vmax=8)
plt.savefig(svnme_reza, dpi=300)
gc.collect()


# make a bar plot of the single value correction ratios
crfs_arr_reza_single = [
    {
        'month': month,
        'crf': crfs_arr_reza_smoothed.sel(month=month).mean().item()
    }
    for month in range(1, 13)
]

# Convert the list of dictionaries to a DataFrame
crfs_arr_reza_single = pd.DataFrame(crfs_arr_reza_single)

# make a bar plot of the single value correction ratios
# Update matplotlib parameters for improved aesthetics
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.serif'] = ['Times New Roman']
mpl.rcParams['font.weight'] = 'bold'
mpl.rcParams['axes.labelweight'] = 'bold'
mpl.rcParams['axes.titleweight'] = 'bold'
mpl.rcParams['xtick.labelsize'] = 18
mpl.rcParams['ytick.labelsize'] = 18
mpl.rcParams['axes.titlesize'] = 18
mpl.rcParams['axes.labelsize'] = 18

# Combine data for both methods
width = 0.4  # Width of each bar
x = np.arange(1, 13)  # Month indices

# Create the bar plot with updated styles
plt.figure(figsize=(12, 6))
plt.bar(x - width / 2, crfs_arr_single['crf'], width, label='Our Method', color='skyblue')
plt.bar(x + width / 2, crfs_arr_reza_single['crf'], width, label='Reza\'s Method', color='orange')

# Add labels and title
plt.xticks(x, 
           ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 
           fontsize=18, fontweight='bold', family='Times New Roman')
plt.xlabel('Month', fontsize=18, fontweight='bold', family='Times New Roman')
plt.ylabel('Correction Ratio', fontsize=18, fontweight='bold', family='Times New Roman')
plt.title('Monthly Correction Ratios Comparison', fontsize=18, fontweight='bold', family='Times New Roman')

# Add grid and legend
plt.grid(axis='y')
plt.legend(fontsize=16, loc='upper right', frameon=True)
plt.tight_layout()

# Save the plot
plt.savefig(os.path.join(path_to_put_plots, f'GPCP_ratios_comparison_{cde_run_dte}.png'), dpi=300)
plt.show()


# - --- -- -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
''''
summarize reza mthods into bulltet points:
- The Reza method calculates correction factors for GPCP precipitation products over Antarctica.
- It uses a quantile-based approach to cap extreme values in the product data.
- A Gaussian filter is applied to smooth the correction factors.
- Zonal averaging is performed to compute the ratio of zonal reference to zonal product.
- The process iterates until the ratio converges within a specified tolerance or a maximum number of iterations is reached.
- The final correction factors are capped to ensure they remain within a defined range (1/CAP to CAP).
- The method is designed to improve the accuracy of GPCP precipitation products over Antarctica by adjusting for biases.

'''