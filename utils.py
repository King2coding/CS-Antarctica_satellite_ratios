#%%
import gc
import os
import pandas as pd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from rasterio.warp import Resampling
from pyproj import CRS
from scipy.io import loadmat
from datetime import date
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.cm import ScalarMappable
from matplotlib import gridspec
import matplotlib as mpl

from scipy.ndimage import gaussian_filter
from scipy.signal import convolve2d

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

imerg_no_data_flag = -9999.9

img_elem = ['precipitation','lat','lon']

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
def plot_correction_ratios(crfs_arr, vmin=None, vmax=None, product_name=None):
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
        gl.xlabel_style = {'fontsize': 16, 'fontweight': 'bold'}
        gl.ylabel_style = {'fontsize': 16, 'fontweight': 'bold'}
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
    if product_name == 'IMERG':
        cbar.ax.set_xticklabels([f"{tick:.3f}" for tick in ticks])
    else:
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

def cf_calculator(reference, target, mask, quantile=1 - 1e-6):
    product_land = np.where(mask, target, np.nan)
    q99 = np.nanquantile(product_land, quantile)
    new_product = np.where(product_land > q99, q99, target)
    new_product = np.where(~mask, target, new_product)
    product_smoothed = apply_filter(new_product)

    return reference / product_smoothed

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def apply_filter(
    array, method="convolution", sigma=1.4, kernel=np.ones((5, 5))
):
    if method == "gaussian":
        new_array = gaussian_filter(array, sigma=(sigma, sigma), order=0)
    elif method == "convolution":
        new_array = convolve2d(array, kernel, boundary="symm", mode="same")
        new_array = new_array / kernel.sum()

    return new_array

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_zonal(spatial_product, mask, y, axis=(0, 1)):
    cosines = np.cos(np.radians(y))[:, np.newaxis]  # Broadcast to match mask shape
    cosines = np.where(mask, cosines, 0)
    weights = cosines / np.nansum(cosines)

    return np.nansum(weights * spatial_product, axis=axis)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def create_xarray(all_precip, all_time_index, lon, lat, attrs=None):
    """
    Create an xarray DataArray from the list of 2D precipitation arrays and add attributes.

    Parameters:
    - all_precip: List or array of 2D precipitation arrays
    - all_time_index: List of timestamps
    - lon: Array of longitudes
    - lat: Array of latitudes
    - attrs: Dictionary of attributes to add to the DataArray (optional)

    Returns:
    - precip_data: xarray DataArray with the specified attributes
    """
    # Create a pandas DatetimeIndex from the list of timestamps
    time_index = pd.to_datetime(all_time_index)
    
    # Create an xarray DataArray from the list of 2D precipitation arrays
    precip_data = xr.DataArray(
        data=all_precip,
        dims=["time", "lat", "lon"],
        coords={
            "time": time_index,
            "lat": lat,
            "lon": lon
        }
    )

    # Add attributes if provided
    if attrs:
        precip_data.attrs.update(attrs)
    
    return precip_data

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def return_imerg_cords(file):
    file_dat = xr.open_dataset(file)
    lon = file_dat.coords['lon'].values
    lat = np.flip(file_dat.coords['lat']).values

    del(file_dat)

    return lon, lat

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def read_nc_imger_file(file_path, product):
    imerg_precip_data = xr.open_dataset(file_path)
    if product == 'imerg_fn':
        precip_aray = imerg_precip_data.precipitation.data 
    elif product == 'imerg_mw':
        precip_aray = imerg_precip_data.MWprecipitation.data 
    precip_aray = np.flip(precip_aray[0,:,:].transpose(), axis=0)
    imerg_time = imerg_precip_data.attrs['BeginDate']
    imerg_precip_data.close()
    
    # Convert time to pandas datetime
    imerg_time_index = pd.to_datetime(imerg_time,format='%Y-%m-%d')

    del(imerg_precip_data,imerg_time)
    
    return precip_aray, imerg_time_index
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def process_imerg(files,product):
    img_lon,img_lat = return_imerg_cords(files[0])

    all_imfn_prcp, all_imfn_tms = [], []

    for imf in files:
        imerg_fn = read_nc_imger_file(imf,product)
        
        all_imfn_prcp.append(imerg_fn[0])
        all_imfn_tms.append(imerg_fn[1])

    # Ensure data is sorted by time
    sorted_indices = np.argsort(np.array(all_imfn_tms))
    all_imfn_prcp = np.array(all_imfn_prcp)[sorted_indices]
    all_imfn_tms = np.array(all_imfn_tms)[sorted_indices]

    # Process the files to aggregate data
    imerg_xarr_data = create_xarray(all_imfn_prcp,all_imfn_tms,img_lon,img_lat)

    # Resample to monthly and calculate the sum
    # imerg_monthly_precip = imerg_xarr_data.resample(time="M").mean()

    return imerg_xarr_data

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def read_hdf_precip_data(file, extract_dims, no_data_flag):

    import h5py

    file_time = [x for x in os.path.split(file)[1].split('.') if x.startswith('20')][0].split('-')[0]

    file_time_index = pd.to_datetime(file_time)

    with h5py.File(file, 'r') as hdf:

        # Extracting the 'precipitation' dataset as an array and orienting it to lat/lon (y,x axis)
        if len(hdf['Grid'][extract_dims[0]][()].shape) == 3:
            precipitation_data_array = np.flip(hdf['Grid'][extract_dims[0]][0][()][:,:].transpose(), axis=0) #precipitation_dataset[()][0, :, :]
        elif len(hdf['Grid'][extract_dims[0]][()].shape) == 2:
            precipitation_data_array = np.flip(hdf['Grid'][extract_dims[0]][()][:,:].transpose(), axis=0)

        # Handling no data flag
        precipitation_data_array = np.where(precipitation_data_array == no_data_flag,
                                            np.nan,precipitation_data_array)        

        # Extract the latitude and longitude datasets
        latitudes = np.flip(hdf['Grid'][extract_dims[1]][:])
        longitudes = hdf['Grid'][extract_dims[2]][:]

        return precipitation_data_array, latitudes, longitudes, file_time_index
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def process_precip_dat(files,dims, resample):
    

    all_prcp_data, all_tms = [], []

    for f in files:
        precip_data = read_hdf_precip_data(f,dims,imerg_no_data_flag)
        
        all_prcp_data.append(precip_data[0])
        all_tms.append(precip_data[3])

    dat_lat, dat_lon = precip_data[1], precip_data[2]

    # Ensure data is sorted by time
    sorted_indices = np.argsort(np.array(all_tms))
    all_prcp_data = np.array(all_prcp_data)[sorted_indices]
    all_tms = np.array(all_tms)[sorted_indices]

    # Process the files to aggregate data
    precip_data_xarr = create_xarray(all_prcp_data,all_tms,dat_lon,dat_lat)  

    if resample == 'yes':
        cc = CRS.from_authority(code=4326,auth_name='EPSG')

        precip_data_xarr.rio.write_crs(cc.to_string(), inplace=True)

        precip_data_xarr = precip_data_xarr.rename({'lon': 'x', 'lat': 'y'})

        precip_data_xarr = precip_data_xarr.rio.reproject(precip_data_xarr.rio.crs, 
                                shape=(360, 720), # set the shape as the autosnow data shape (360, 720)
                                resampling=Resampling.nearest,) 
        
        precip_data_xarr = precip_data_xarr.rename({'x': 'lon', 'y': 'lat'})

    return precip_data_xarr

# %%
