"""
Main corrector class for Antarctica GPCP precipitation correction.
"""

import os
import numpy as np
import pandas as pd
import xarray as xr
from scipy.io import loadmat
from datetime import date

from .utils import (
    ds_swaplon, cf_calculator, cf_smoother, apply_cap, apply_filter
)
from .plotting import plot_correction_ratios, plot_monthly_comparison


class GPCPCorrector:
    """
    Main class for computing GPCP precipitation correction ratios over Antarctica.
    
    This class handles the loading of CloudSat and GPCP data, applies land masks,
    and computes correction ratios using multiple methods.
    """
    
    def __init__(self, cs_data_path, gpcp_data_path, mask_path, output_path=None):
        """
        Initialize the GPCP corrector.
        
        Parameters:
        -----------
        cs_data_path : str
            Path to CloudSat-Antarctica climatology data
        gpcp_data_path : str
            Path to GPCP monthly data
        mask_path : str
            Path to land/ocean mask file
        output_path : str, optional
            Path for saving outputs
        """
        self.cs_data_path = cs_data_path
        self.gpcp_data_path = gpcp_data_path
        self.mask_path = mask_path
        self.output_path = output_path or "./outputs"
        
        # Initialize data containers
        self.cs_data = None
        self.gpcp_data = None
        self.mask = None
        self.cs_monthly_clim = None
        self.gpcp_monthly_clim = None
        
        # Ensure output directory exists
        os.makedirs(self.output_path, exist_ok=True)
    
    def load_mask(self):
        """Load and process the land/ocean mask for Antarctica."""
        print("Loading land/ocean mask...")
        mask_data = loadmat(self.mask_path)["mask50"][-60:, :].swapaxes(0, 1)
        mask_data = np.flip(mask_data, axis=1)
        mask_binary = mask_data < 75
        
        # Reorder mask for proper longitude alignment
        new_mask = mask_binary.copy()
        new_mask[:360, :] = mask_binary[360:, :].copy()
        new_mask[360:, :] = mask_binary[:360, :].copy()
        self.mask = np.flip(new_mask.T, axis=0).astype(int)
        
        return self.mask
    
    def load_cloudsat_data(self):
        """Load CloudSat-Antarctica monthly climatology data."""
        print("Loading CloudSat-Antarctica data...")
        cs_file = os.path.join(self.cs_data_path, 
                              'CS-Antarctica_monthly_climatology_2007-2010.nc')
        self.cs_data = xr.open_dataarray(cs_file, engine='netcdf4')
        
        if self.mask is None:
            self.load_mask()
        
        # Apply mask and rename time dimension
        self.cs_monthly_clim = self.cs_data.where(self.mask == 1)
        self.cs_monthly_clim = self.cs_monthly_clim.rename({'time': 'month'})
        
        return self.cs_monthly_clim
    
    def load_gpcp_data(self, years=['2007', '2008', '2009', '2010']):
        """
        Load GPCP monthly data for specified years.
        
        Parameters:
        -----------
        years : list
            List of years to load (default: 2007-2010)
        """
        print("Loading GPCP data...")
        
        # Find GPCP files for specified years
        gpcp_files = [
            os.path.join(self.gpcp_data_path, f)
            for f in os.listdir(self.gpcp_data_path)
            if f.startswith('GPCPMON_L3') and f.split('_')[2][:4] in years
            and f.endswith('.nc4')
        ]
        
        if not gpcp_files:
            raise FileNotFoundError(f"No GPCP files found for years {years}")
        
        # Load and process GPCP data
        self.gpcp_data = xr.open_mfdataset(gpcp_files, combine='by_coords', 
                                          engine='netcdf4')
        self.gpcp_data = ds_swaplon(self.gpcp_data)
        
        # Calculate monthly climatology
        gpcp_monthly_clim = (self.gpcp_data['sat_gauge_precip']
                           .groupby('time.month').mean(dim='time').compute())
        
        # Subset over Antarctica and apply mask
        if self.mask is None:
            self.load_mask()
            
        self.gpcp_monthly_clim = (gpcp_monthly_clim
                                .isel(latitude=slice(-60, None))
                                .where(self.mask == 1))
        
        return self.gpcp_monthly_clim
    
    def align_datasets(self):
        """Align CloudSat and GPCP datasets for comparison."""
        if self.cs_monthly_clim is None:
            self.load_cloudsat_data()
        if self.gpcp_monthly_clim is None:
            self.load_gpcp_data()
        
        # Interpolate CloudSat data to GPCP grid
        self.cs_monthly_clim_aligned = self.cs_monthly_clim.interp(
            lat=self.gpcp_monthly_clim.latitude,
            lon=self.gpcp_monthly_clim.longitude
        )
        
        return self.cs_monthly_clim_aligned, self.gpcp_monthly_clim
    
    def compute_direct_ratios(self):
        """
        Compute correction ratios using direct division method.
        
        Returns:
        --------
        xarray.DataArray
            Monthly correction ratios
        """
        print("Computing direct correction ratios...")
        
        if not hasattr(self, 'cs_monthly_clim_aligned'):
            self.align_datasets()
        
        # Calculate monthly ratios
        monthly_ratios = {}
        for month in range(1, 13):
            gpcp_month = self.gpcp_monthly_clim.sel(month=month)
            cs_month = self.cs_monthly_clim_aligned.sel(month=month)
            monthly_ratios[month] = cs_month / gpcp_month
        
        # Convert to DataArray
        self.direct_ratios = xr.concat(
            [monthly_ratios[m] for m in range(1, 13)], dim='month'
        )
        self.direct_ratios = self.direct_ratios.assign_coords(
            month=list(range(1, 13))
        )
        
        return self.direct_ratios
    
    def compute_reza_ratios(self, quantile=1-1e-6, cap=3):
        """
        Compute correction ratios using Reza's smoothing method.
        
        Parameters:
        -----------
        quantile : float
            Quantile threshold for extreme value capping
        cap : float
            Maximum cap value for correction ratios
            
        Returns:
        --------
        xarray.DataArray
            Smoothed monthly correction ratios
        """
        print("Computing Reza method correction ratios...")
        
        if not hasattr(self, 'cs_monthly_clim_aligned'):
            self.align_datasets()
        
        # Calculate initial correction factors
        reza_ratios = xr.concat([
            xr.DataArray(
                cf_calculator(
                    self.cs_monthly_clim_aligned.sel(month=month).values,
                    self.gpcp_monthly_clim.sel(month=month).values,
                    self.mask,
                    quantile
                ),
                dims=["latitude", "longitude"],
                coords={
                    "latitude": self.gpcp_monthly_clim.latitude,
                    "longitude": self.gpcp_monthly_clim.longitude,
                    "month": month,
                },
            )
            for month in range(1, 13)
        ], dim="month")
        
        # Apply smoothing and zonal averaging
        self.reza_ratios = xr.concat([
            xr.DataArray(
                cf_smoother(
                    self.cs_monthly_clim_aligned.sel(month=month).values,
                    self.gpcp_monthly_clim.sel(month=month).values,
                    reza_ratios.sel(month=month).values,
                    self.mask,
                    self.gpcp_monthly_clim.latitude.values,
                    cap
                ),
                dims=["latitude", "longitude"],
                coords={
                    "latitude": self.gpcp_monthly_clim.latitude,
                    "longitude": self.gpcp_monthly_clim.longitude,
                    "month": month,
                },
            )
            for month in range(1, 13)
        ], dim="month")
        
        self.reza_ratios = self.reza_ratios.assign_coords(
            month=list(range(1, 13))
        )
        
        return self.reza_ratios
    
    def get_single_value_ratios(self, method='direct'):
        """
        Calculate spatially-averaged single value correction ratios.
        
        Parameters:
        -----------
        method : str
            Method to use ('direct' or 'reza')
            
        Returns:
        --------
        pandas.DataFrame
            Monthly single-value correction ratios
        """
        if method == 'direct':
            if not hasattr(self, 'direct_ratios'):
                self.compute_direct_ratios()
            ratios_data = self.direct_ratios
        elif method == 'reza':
            if not hasattr(self, 'reza_ratios'):
                self.compute_reza_ratios()
            ratios_data = self.reza_ratios
        else:
            raise ValueError("Method must be 'direct' or 'reza'")
        
        single_ratios = [
            {
                'month': month,
                'crf': ratios_data.sel(month=month).mean(
                    dim=['latitude', 'longitude'], skipna=True
                ).item()
            }
            for month in range(1, 13)
        ]
        
        return pd.DataFrame(single_ratios)
    
    def save_results(self, ratios_data, filename_suffix="", method="direct"):
        """
        Save correction ratios to NetCDF file.
        
        Parameters:
        -----------
        ratios_data : xarray.DataArray
            Correction ratios to save
        filename_suffix : str
            Suffix for filename
        method : str
            Method name for filename
        """
        today = date.today().strftime('%Y%m%d')
        filename = f'GPCP_correction_ratios_{method}_{today}{filename_suffix}.nc'
        filepath = os.path.join(self.output_path, filename)
        
        ratios_data.to_netcdf(filepath)
        print(f"Results saved to: {filepath}")
        
        return filepath
    
    def generate_plots(self, ratios_data, method_name="", save_plots=True):
        """
        Generate and optionally save plots of correction ratios.
        
        Parameters:
        -----------
        ratios_data : xarray.DataArray
            Correction ratios to plot
        method_name : str
            Method name for plot titles
        save_plots : bool
            Whether to save plots to disk
            
        Returns:
        --------
        matplotlib.figure.Figure
            The generated figure
        """
        today = date.today().strftime('%Y%m%d')
        
        if save_plots:
            save_path = os.path.join(
                self.output_path, 
                f'GPCP_ratios_{method_name}_{today}.png'
            )
        else:
            save_path = None
        
        fig = plot_correction_ratios(
            ratios_data, 
            vmin=0, 
            vmax=8,
            save_path=save_path,
            title_suffix=method_name
        )
        
        return fig
    
    def run_full_analysis(self, save_results=True, save_plots=True):
        """
        Run complete analysis with both methods.
        
        Parameters:
        -----------
        save_results : bool
            Whether to save results to NetCDF files
        save_plots : bool
            Whether to save plots
            
        Returns:
        --------
        dict
            Dictionary containing all results
        """
        print("Starting full GPCP correction analysis...")
        
        # Compute both methods
        direct_ratios = self.compute_direct_ratios()
        reza_ratios = self.compute_reza_ratios()
        
        # Get single value ratios
        direct_single = self.get_single_value_ratios('direct')
        reza_single = self.get_single_value_ratios('reza')
        
        # Save results if requested
        if save_results:
            self.save_results(direct_ratios, method="direct")
            self.save_results(reza_ratios, method="reza")
        
        # Generate plots if requested
        if save_plots:
            self.generate_plots(direct_ratios, "Direct Method", save_plots)
            self.generate_plots(reza_ratios, "Reza Method", save_plots)
            
            # Comparison plot
            today = date.today().strftime('%Y%m%d')
            comparison_path = os.path.join(
                self.output_path, 
                f'GPCP_ratios_comparison_{today}.png'
            )
            plot_monthly_comparison(
                direct_single['crf'].values,
                reza_single['crf'].values,
                labels=['Direct Method', "Reza's Method"],
                save_path=comparison_path
            )
        
        results = {
            'direct_ratios': direct_ratios,
            'reza_ratios': reza_ratios,
            'direct_single': direct_single,
            'reza_single': reza_single,
            'cloudsat_data': self.cs_monthly_clim_aligned,
            'gpcp_data': self.gpcp_monthly_clim,
            'mask': self.mask
        }
        
        print("Analysis complete!")
        return results
