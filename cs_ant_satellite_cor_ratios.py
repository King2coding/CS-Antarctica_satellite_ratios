#%%
'''
This script is designed to compute correction ratios for GPCP precipitation products, specifically tailored for Antarctica's land regions. 
The correction process leverages CloudSat-Antarctica climatology data (2007-2010) augmented with ERA5 data. 
The output includes 12 monthly correction ratios or factors represented as array maps, as well as single ratio values. 
These correction ratios can be applied to adjust GPCP precipitation products for improved accuracy over Antarctica.
'''

#%%
from utils import *

#%% Define the path to the input data
cs_ant_month_clim_path = r'/ra1/pubdat/AVHRR_CloudSat_proj/CS_Antartica_analysis_kkk/CS-Antarctica_maps'
gpcp_v3pt3_data_path = r'/ra1/pubdat/Satellite_eval_over_Oceans/data/GPCP/GPCP_v3_pnt_3_monthly'
gpcp_v3pt2_data_path = r'/ra1/pubdat/Satellite_eval_over_Oceans/data/GPCP/GPCP_v3_pnt2_monthly'
imerg_v7_data_path = r'/ra1/pubdat/AVHRR_CloudSat_proj/IMERG/IMERGV7_monthly'
path_to_put_ratio_maps = r'/home/kkumah/Projects/CS-Antarctica_satellite_ratios/ratio_maps'
path_to_put_ratio_dfs = r'/home/kkumah/Projects/CS-Antarctica_satellite_ratios/ratio_dfs'
path_to_put_plots = r'/home/kkumah/Projects/CS-Antarctica_satellite_ratios/GPCP_ratios/plots'

#%% Load the data
gpcp_v3pt3_files_2007_2010 = sorted([
    os.path.join(gpcp_v3pt3_data_path, f) 
    for f in os.listdir(gpcp_v3pt3_data_path) 
    if f.startswith('GPCPMON_L3') and f.split('_')[2][:4] in ['2007', '2008', '2009', '2010'] \
    and f.endswith('.nc4')
])

gpcp_v3pt3_data = xr.open_mfdataset(gpcp_v3pt3_files_2007_2010, combine='by_coords', engine='netcdf4')
gpcp_v3pt3_data = ds_swaplon(gpcp_v3pt3_data)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

gpcp_v3pt2_files_2007_2010 = sorted([
    os.path.join(gpcp_v3pt2_data_path, f) 
    for f in os.listdir(gpcp_v3pt2_data_path) 
    if f.startswith('GPCPMON_L3') and f.split('_')[2][:4] in ['2007', '2008', '2009', '2010'] \
    and f.endswith('.nc4')
])
gpcp_v3pt2_data = xr.open_mfdataset(gpcp_v3pt2_files_2007_2010, combine='by_coords', engine='netcdf4')
gpcp_v3pt2_data = ds_swaplon(gpcp_v3pt2_data)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

imerg_v7_files_2007_2010 = sorted([
    os.path.join(imerg_v7_data_path, f) 
    for f in os.listdir(imerg_v7_data_path) 
    if f.startswith('3B-MO.MS.MRG.3IMERG') and f.split('.')[4][:4] in ['2007', '2008', '2009', '2010'] \
    and f.endswith('.HDF5')
])
# imerg_v7_data = xr.open_mfdataset(imerg_v7_files_2007_2010, combine='by_coords', engine='netcdf4')
# imerg_v7_data = ds_swaplon(imerg_v7_data)
imerg_v7_data =  process_precip_dat(imerg_v7_files_2007_2010, img_elem, 'yes')
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

cs_ant_mnth_clim_filenme = os.path.join(cs_ant_month_clim_path, 'CS-Antarctica_monthly_climatology_2007-2010.nc') 
cs_ant_month_clim = xr.open_dataarray(cs_ant_mnth_clim_filenme, engine='netcdf4')
cs_ant_month_clim = cs_ant_month_clim.where(new_mask_ == 1)

gc.collect()
#%%
# Calculate monthly climatology from GPCP data
gpcp_v3pt3_monthly_clim = gpcp_v3pt3_data['sat_gauge_precip'].groupby('time.month').mean(dim='time').compute()

# Subset the data over Antarctica
gpcp_v3pt3_ant_monthly_clim = gpcp_v3pt3_monthly_clim.isel(latitude=slice(-60, None)).where(new_mask_ == 1)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

cs_ant_month_clim_aligned = cs_ant_month_clim.rename({'time': 'month',
                                                      'lat': 'latitude',
                                                      'lon': 'longitude'})

# Ensure latitude and longitude dimensions match
cs_ant_month_clim_aligned = cs_ant_month_clim_aligned.drop(['lat', 'lon'], errors='ignore').interp(
    latitude=gpcp_v3pt3_ant_monthly_clim.latitude, 
    longitude=gpcp_v3pt3_ant_monthly_clim.longitude
).squeeze()

# plot and save the monthly climatology data

plot_correction_ratios(cs_ant_month_clim_aligned, vmin=0, vmax=1.5)
svnme = os.path.join(path_to_put_plots, f'CS_Antarctica_monthly_clim_{cde_run_dte}.png')
plt.savefig(svnme, dpi=500)
gc.collect()
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Plot the monthly climatology data
plot_correction_ratios(gpcp_v3pt3_ant_monthly_clim, vmin=0, vmax=1.5)
svnme = os.path.join(path_to_put_plots, f'GPCP_v3pt3_monthly_clim_{cde_run_dte}.png')
plt.savefig(svnme, dpi=500)
gc.collect()

# Calculate monthly climatology from GPCP v3.2 data
gpcp_v3pt2_monthly_clim = gpcp_v3pt2_data['sat_gauge_precip'].groupby('time.month').mean(dim='time').compute()

# Subset the data over Antarctica
gpcp_v3pt2_ant_monthly_clim = gpcp_v3pt2_monthly_clim.isel(latitude=slice(-60, None)).where(new_mask_ == 1)

# Plot the monthly climatology data
plot_correction_ratios(gpcp_v3pt2_ant_monthly_clim, vmin=0, vmax=1.5,)
svnme = os.path.join(path_to_put_plots, f'GPCP_v3pt2_monthly_clim_{cde_run_dte}.png')
plt.savefig(svnme, dpi=500)
gc.collect()

# Calculate monthly climatology from IMERG v7 data
imerg_v7_monthly_clim = imerg_v7_data.groupby('time.month').mean(dim='time').compute()

# Subset the data over Antarctica
imerg_v7_ant_monthly_clim = imerg_v7_monthly_clim.isel(lat=slice(-60, None)).where(new_mask_ == 1)

# Plot the monthly climatology data
plot_correction_ratios(imerg_v7_ant_monthly_clim, vmin=0, vmax=0.009, product_name='IMERG')
svnme = os.path.join(path_to_put_plots, f'IMERG_v7_monthly_clim_{cde_run_dte}.png')
plt.savefig(svnme, dpi=500)
gc.collect()

#%% Calculate correction ratios
# Compute correction ratios for each month pair
# Perform the division lazily using Dask
# Ensure the dimensions align correctly before division

# Compute correction ratios for GPCP v3.3 data
# gpcp_v3pt3_ratios = compute_monthly_ratios(cs_ant_month_clim_aligned, gpcp_v3pt3_ant_monthly_clim)
# Apply quantile-based outlier removal/correction 
# Apply spatial smoothing
gpcp_v3pt3_ratios = xr.concat(
    [
        xr.DataArray(
            cf_calculator(
                cs_ant_month_clim_aligned.sel(month=month).values,
                gpcp_v3pt3_ant_monthly_clim.sel(month=month).values,
                new_mask_,
            ),
            dims=["latitude", "longitude"],
            coords={
                "latitude": gpcp_v3pt3_ant_monthly_clim.latitude,
                "longitude": gpcp_v3pt3_ant_monthly_clim.longitude,
                "month": month,
            },
        )
        for month in range(1, 13)
    ],
    dim="month",
)
gpcp_v3pt3_ratios = gpcp_v3pt3_ratios.assign_coords(month=list(range(1, 13)))
# save the correction ratios to a netCDF file
gpcp_v3pt3_ratios.to_netcdf(os.path.join(path_to_put_ratio_maps, f'gpcp_v3pt3_ratios_{cde_run_dte}.nc'))

# Plot the correction ratios for GPCP v3.3 data
print("Plotting correction ratios for GPCP v3.3 data...")
svnme = os.path.join(path_to_put_plots, f'GPCP_v3pt3_ratios_{cde_run_dte}.png')
plot_correction_ratios(gpcp_v3pt3_ratios)
plt.savefig(svnme, dpi=500)
gc.collect()
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Compute correction ratios for GPCP v3.2 data
# gpcp_v3pt2_ratios = compute_monthly_ratios(cs_ant_month_clim_aligned, gpcp_v3pt2_ant_monthly_clim)
gpcp_v3pt2_ratios = xr.concat(
    [
        xr.DataArray(
            cf_calculator(
                cs_ant_month_clim_aligned.sel(month=month).values,
                gpcp_v3pt2_ant_monthly_clim.sel(month=month).values,
                new_mask_,
            ),
            dims=["latitude", "longitude"],
            coords={
                "latitude": gpcp_v3pt2_ant_monthly_clim.latitude,
                "longitude": gpcp_v3pt2_ant_monthly_clim.longitude,
                "month": month,
            },
        )
        for month in range(1, 13)
    ],
    dim="month",
)
gpcp_v3pt2_ratios = gpcp_v3pt2_ratios.assign_coords(month=list(range(1, 13)))
# save the correction ratios to a netCDF file
gpcp_v3pt2_ratios.to_netcdf(os.path.join(path_to_put_ratio_maps, f'gpcp_v3pt2_ratios_{cde_run_dte}.nc'))
print("Plotting correction ratios for GPCP v3.2 data...")
# Plot the correction ratios for GPCP v3.2 data
svnme = os.path.join(path_to_put_plots, f'GPCP_v3pt2_ratios_{cde_run_dte}.png')
plot_correction_ratios(gpcp_v3pt2_ratios)
plt.savefig(svnme, dpi=500)
gc.collect()

# Compute correction ratios for IMERG v7 data
# imerg_v7_ratios = compute_monthly_ratios(cs_ant_month_clim_aligned, imerg_v7_ant_monthly_clim)
imerg_v7_ratios = xr.concat(
    [
        xr.DataArray(
            cf_calculator(
                cs_ant_month_clim_aligned.sel(month=month).values,
                imerg_v7_ant_monthly_clim.sel(month=month).values,
                new_mask_,
            ),
            dims=["latitude", "longitude"],
            coords={
                "latitude": imerg_v7_ant_monthly_clim.lat.values,
                "longitude": imerg_v7_ant_monthly_clim.lon.values,
                "month": month,
            },
        )
        for month in range(1, 13)
    ],
    dim="month",
)
imerg_v7_ratios = imerg_v7_ratios.assign_coords(month=list(range(1, 13)))
# save the correction ratios to a netCDF file
imerg_v7_ratios.to_netcdf(os.path.join(path_to_put_ratio_maps, f'imerg_v7_ratios_{cde_run_dte}.nc'))
print("Plotting correction ratios for IMERG v7 data...")
# Plot the correction ratios for IMERG v7 data
svnme = os.path.join(path_to_put_plots, f'IMERG_v7_ratios_{cde_run_dte}.png')
# mn,mx = imerg_v7_ratios.min().item(), imerg_v7_ratios.max().item()
plot_correction_ratios(imerg_v7_ratios, vmin = 10, vmax=2000, product_name='IMERG')
plt.savefig(svnme, dpi=500)
gc.collect()

# %% calculate single value correction ratios
# Calculate single value correction ratios and store them in a DataFrame
# First we need to Apply zonal cosine weights to each of the 12 monthly maps
gpcp_v3pt3_zonal_weighted = xr.concat(
    [
        xr.DataArray(
            get_zonal(
                gpcp_v3pt3_ant_monthly_clim.sel(month=month), 
                new_mask_, 
                gpcp_v3pt3_ant_monthly_clim.latitude.values, 
                axis=(0, 1)
            ),
            dims=["latitude"],
            coords={"latitude": gpcp_v3pt3_ant_monthly_clim.latitude, "month": month},
        )
        for month in range(1, 13)
    ],
    dim="month",
)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Compute zonal weighted data for GPCP v3.2
gpcp_v3pt2_zonal_weighted = xr.concat(
    [
        xr.DataArray(
            get_zonal(
                gpcp_v3pt2_ant_monthly_clim.sel(month=month), 
                new_mask_, 
                gpcp_v3pt2_ant_monthly_clim.latitude.values, 
                axis=(0, 1)
            ),
            dims=["latitude"],
            coords={"latitude": gpcp_v3pt2_ant_monthly_clim.latitude, "month": month},
        )
        for month in range(1, 13)
    ],
    dim="month",
)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Compute zonal weighted data for IMERG v7
imerg_v7_zonal_weighted = xr.concat(
    [
        xr.DataArray(
            get_zonal(
                imerg_v7_ant_monthly_clim.sel(month=month), 
                new_mask_, 
                imerg_v7_ant_monthly_clim.lat.values, 
                axis=(0, 1)
            ),
            dims=["lat"],
            coords={"lat": imerg_v7_ant_monthly_clim.lat, "month": month},
        )
        for month in range(1, 13)
    ],
    dim="month",
)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Compute zonal weighted data for CloudSat Antarctica
cs_ant_zonal_weighted = xr.concat(
    [
        xr.DataArray(
            get_zonal(
                cs_ant_month_clim_aligned.sel(month=month), 
                new_mask_, 
                cs_ant_month_clim_aligned.latitude.values, 
                axis=(0, 1)
            ),
            dims=["latitude"],
            coords={"latitude": cs_ant_month_clim_aligned.latitude, "month": month},
        )
        for month in range(1, 13)
    ],
    dim="month",
)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# now compute the single value correction ratios and convert to DataFrame

gpcp_v3pt3_crfs_arr_single = [
    {
        'month': month,
        'crf': (cs_ant_zonal_weighted.sel(month=month).mean().item() /
                gpcp_v3pt3_zonal_weighted.sel(month=month).mean().item())
    }
    for month in range(1, 13)
]

# Convert the list of dictionaries to a DataFrame
gpcp_v3pt3_crfs_arr_single = pd.DataFrame(gpcp_v3pt3_crfs_arr_single)
# save the single value correction ratios to a csv file
gpcp_v3pt3_crfs_arr_single.to_csv(os.path.join(path_to_put_ratio_dfs, f'gpcp_v3pt3_crfs_{cde_run_dte}.csv'), index=False)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

gpcp_v3pt2_crfs_arr_single = [
    {
        'month': month,
        'crf': (cs_ant_zonal_weighted.sel(month=month).mean().item() /
                gpcp_v3pt2_zonal_weighted.sel(month=month).mean().item())
    }
    for month in range(1, 13)
]

# Convert the list of dictionaries to a DataFrame
gpcp_v3pt2_crfs_arr_single = pd.DataFrame(gpcp_v3pt2_crfs_arr_single)
# save the single value correction ratios to a csv file
gpcp_v3pt2_crfs_arr_single.to_csv(os.path.join(path_to_put_ratio_dfs, f'gpcp_v3pt2_crfs_{cde_run_dte}.csv'), index=False)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

imerg_v7_crfs_arr_single = [
    {
        'month': month,
        'crf': (cs_ant_zonal_weighted.sel(month=month).mean().item() /
                imerg_v7_zonal_weighted.sel(month=month).mean().item())
    }
    for month in range(1, 13)
]
# Convert the list of dictionaries to a DataFrame
imerg_v7_crfs_arr_single = pd.DataFrame(imerg_v7_crfs_arr_single)
# save the single value correction ratios to a csv file
imerg_v7_crfs_arr_single.to_csv(os.path.join(path_to_put_ratio_dfs, f'imerg_v7_crfs_{cde_run_dte}.csv'), index=False)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# E compute AIRS CS ratios as GPCP ratios * 1.4
airs_cs_crfs_arr_single = gpcp_v3pt3_crfs_arr_single.copy()
airs_cs_crfs_arr_single['crf'] = airs_cs_crfs_arr_single['crf'] * 1.4

# save the single value correction ratios to a csv file
airs_cs_crfs_arr_single.to_csv(os.path.join(path_to_put_ratio_dfs, f'airs_cs_crfs_{cde_run_dte}.csv'), index=False)

#%% Do bar plot comparion of the single value correction ratios for diff products

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
width = 0.4  # Width of each bar
x = np.arange(1, 13)  # Month indices
plt.figure(figsize=(10, 6))
# plt.bar(x - width / 2, gpcp_v3pt3_crfs_arr_single['crf'], width, label='GPCP v3.3', color='skyblue')
# plt.bar(x + width / 2, gpcp_v3pt2_crfs_arr_single['crf'], width, label='GPCP v3.2', color='orange')

plt.bar(x - width / 2, gpcp_v3pt3_crfs_arr_single['crf']*1.4, width, label='GPCP v3.3', color='skyblue')
plt.bar(x + width / 2, gpcp_v3pt2_crfs_arr_single['crf']*1.4, width, label='GPCP v3.2', color='orange')


plt.xticks(gpcp_v3pt3_crfs_arr_single['month'], 
           ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 
           fontsize=18, fontweight='bold', family='Times New Roman')
# plt.ylim(0, 1.2)  # Adjust y-axis scale to match the previous plots

plt.xlabel('Month', fontsize=18, fontweight='bold', family='Times New Roman')
plt.ylabel('Correction Ratio', fontsize=18, fontweight='bold', family='Times New Roman')
plt.title('Single Value Correction Ratios', fontsize=18, fontweight='bold', family='Times New Roman')
plt.grid(axis='y', ls='--', lw=0.5, c='gray', alpha=0.5)
plt.tight_layout()

# Add grid and legend
# plt.grid(axis='y')
plt.legend(fontsize=16, loc='best', frameon=False)
plt.tight_layout()


# Save the plot
plt.savefig(os.path.join(path_to_put_plots, f'GPCP_ratios_single_{cde_run_dte}.png'), dpi=300)
plt.show()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# make a similar plot for a single zonal correction ratio
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
plt.bar(imerg_v7_crfs_arr_single['month'], imerg_v7_crfs_arr_single['crf'], color='skyblue')
plt.xticks(imerg_v7_crfs_arr_single['month'], 
           ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 
           fontsize=18, fontweight='bold', family='Times New Roman')
plt.xlabel('Month', fontsize=18, fontweight='bold', family='Times New Roman')
plt.ylabel('Correction Ratio', fontsize=18, fontweight='bold', family='Times New Roman')
plt.title('Single Value Correction Ratios for IMERG', fontsize=18, fontweight='bold', family='Times New Roman')
plt.ylim(100, 650)  # Adjust y-axis scale to match the previous plots
plt.grid(axis='y')
plt.tight_layout()

# Save the plot
plt.savefig(os.path.join(path_to_put_plots, f'IMERG_ratios_single_zon_{cde_run_dte}.png'), dpi=300)
plt.show()

#%%
# lets compute and compare zonal means to 

#%%
# Compute zonal means for CloudSat Antarctica climatology data
# Compute zonal means for CloudSat Antarctica climatology data
cs_ant_month_clim_zonal = cs_ant_month_clim_aligned.groupby('latitude').mean(dim=['month', 'longitude'], skipna=True).to_dataframe(name='mean_value').reset_index()

# Compute zonal means for GPCP v3.3 data
gpcp_v3pt3_monthly_clim_zonal = gpcp_v3pt3_ant_monthly_clim.groupby('latitude').mean(dim=['month', 'longitude'], skipna=True).to_dataframe(name='mean_value').reset_index()

# Compute zonal means for GPCP v3.2 data
gpcp_v3pt2_monthly_clim_zonal = gpcp_v3pt2_ant_monthly_clim.groupby('latitude').mean(dim=['month', 'longitude'], skipna=True).to_dataframe(name='mean_value').reset_index()

# Compute zonal means for IMERG v7 data
imerg_v7_monthly_clim_zonal = imerg_v7_ant_monthly_clim.groupby('lat').mean(dim=['month', 'lon'], skipna=True).to_dataframe(name='mean_value').reset_index()

# plot the zonal means to compare products
# place lat in the y axis and mean values on x axis
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.serif'] = ['Times New Roman']
mpl.rcParams['font.weight'] = 'bold'
mpl.rcParams['axes.labelweight'] = 'bold'
mpl.rcParams['axes.titleweight'] = 'bold'
mpl.rcParams['xtick.labelsize'] = 18
mpl.rcParams['ytick.labelsize'] = 18
mpl.rcParams['axes.titlesize'] = 18
mpl.rcParams['axes.labelsize'] = 18

plt.figure(figsize=(10, 6))
plt.plot(cs_ant_month_clim_zonal.query('latitude <= -68')['mean_value'], 
         cs_ant_month_clim_zonal.query('latitude <= -68')['latitude'], 
         label='CloudSat Antarctica')
plt.plot(gpcp_v3pt3_monthly_clim_zonal.query('latitude <= -68')['mean_value'], 
         gpcp_v3pt3_monthly_clim_zonal.query('latitude <= -68')['latitude'], 
         label='GPCP v3.3')
plt.plot(gpcp_v3pt2_monthly_clim_zonal.query('latitude <= -68')['mean_value'], 
         gpcp_v3pt2_monthly_clim_zonal.query('latitude <= -68')['latitude'], 
         label='GPCP v3.2')
plt.plot(imerg_v7_monthly_clim_zonal.query('lat <= -68')['mean_value'], 
         imerg_v7_monthly_clim_zonal.query('lat <= -68')['lat'], 
         label='IMERG v7')
plt.xlabel('Latitude', fontsize=18, fontweight='bold')
plt.ylabel('Mean Value', fontsize=18, fontweight='bold')
plt.title('Zonal Means for CloudSat Antarctica, GPCP v3.3,\n GPCP v3.2, and IMERG v7', fontsize=18, fontweight='bold')
plt.xticks(fontsize=18, fontweight='bold')
plt.yticks(fontsize=18, fontweight='bold')
plt.grid(which='major', axis='both', ls='--', lw=0.5, c='gray', alpha=0.5)
plt.legend(frameon=False, fontsize=18)

plt.tight_layout()

# Save the plot
plt.savefig(os.path.join(path_to_put_plots, f'zonal_means_comparison_{cde_run_dte}.png'), 
            dpi=300, bbox_inches='tight')
plt.show()
#%%
# Convert the list of dictionaries to a DataFrame
crfs_arr_single_zon = pd.DataFrame(crfs_arr_single_zon)

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
plt.bar(crfs_arr_single_zon['month'], crfs_arr_single_zon['crf'], color='skyblue')
plt.xticks(crfs_arr_single_zon['month'], 
           ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 
           fontsize=18, fontweight='bold', family='Times New Roman')
plt.xlabel('Month', fontsize=18, fontweight='bold', family='Times New Roman')
plt.ylabel('Correction Ratio', fontsize=18, fontweight='bold', family='Times New Roman')
plt.title('Monthly Correction Ratios for GPCP Precipitation Products', fontsize=18, fontweight='bold', family='Times New Roman')
plt.ylim(0, 1.2)  # Adjust y-axis scale to match the previous plots
plt.grid(axis='y')
plt.tight_layout()

# Save the plot
plt.savefig(os.path.join(path_to_put_plots, f'GPCP_ratios_single_zon_{cde_run_dte}.png'), dpi=300)
plt.show()

#%% Reza method


CAP = 3


def apply_cap(array, minimum=1 / CAP, maximum=CAP):
    temp = np.where(array > maximum, maximum, array)
    temp = np.where(temp < minimum, minimum, temp)

    return temp


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