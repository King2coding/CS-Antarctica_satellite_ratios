"""
Plotting functions for Antarctica precipitation correction visualization.
"""

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.cm import ScalarMappable
from matplotlib import gridspec


def plot_correction_ratios(crfs_arr, vmin=None, vmax=None, save_path=None, title_suffix=""):
    """
    Plot correction ratios for each month in a 3x4 grid.

    Parameters:
    -----------
    crfs_arr : xarray.DataArray
        Correction ratios with dimensions (month, latitude, longitude)
    vmin : float, optional
        Minimum value for colormap
    vmax : float, optional
        Maximum value for colormap
    save_path : str, optional
        Path to save the plot
    title_suffix : str, optional
        Suffix to add to plot title
        
    Returns:
    --------
    matplotlib.figure.Figure
        The created figure
    """
    proj = ccrs.SouthPolarStereo()

    # Define the custom colormap
    try:
        mpl_cm = plt.cm.get_cmap("nipy_spectral", 21)
    except AttributeError:
        # For newer matplotlib versions
        import matplotlib.colormaps as cmaps
        mpl_cm = cmaps.get_cmap("nipy_spectral").resampled(21)
    
    ncolors = mpl_cm(np.linspace(0, 1, 21))[:20]
    ncolors[0] = [128 / 256, 100 / 256, 128 / 256, 1]
    ncolors[2] = ncolors[1].copy()
    ncolors[1] = [0.7, 0.1, 0.7, 1]
    newcmap = ListedColormap(ncolors)

    # Set discrete color levels
    vmin = vmin or 0
    vmax = vmax or 8
    levels = np.linspace(vmin, vmax, len(ncolors))
    norm = BoundaryNorm(levels, newcmap.N)

    # Create a GridSpec with optimized spacing
    fig = plt.figure(figsize=(20, 15))
    gs = gridspec.GridSpec(3, 4, figure=fig, wspace=0.025, hspace=0.2)

    month_names = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", 
                   "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    
    for month in range(1, 13):
        ax = fig.add_subplot(gs[month - 1], projection=proj)
        ax.set_extent([-180, 180, -90, -65], ccrs.PlateCarree())
        ax.coastlines(lw=0.25, resolution="110m", zorder=2)

        # Plot the correction ratio for the current month
        crf = crfs_arr.sel(month=month)
        crf.plot(ax=ax, transform=ccrs.PlateCarree(), 
                vmin=vmin, vmax=vmax, cmap=newcmap, norm=norm, 
                add_colorbar=False, add_labels=False)

        ax.add_feature(cfeature.OCEAN, zorder=1, edgecolor=None, 
                      lw=0, color="silver", alpha=0.5)
        
        # Place month title in upper right corner of each subplot
        ax.text(0.95, 0.95, month_names[month - 1], 
                transform=ax.transAxes, 
                fontsize=16, fontweight='bold',
                ha='right', va='top',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                         alpha=0.8, edgecolor='none'))

        # Add gridlines with improved positioning
        gl = ax.gridlines(draw_labels=True, x_inline=False, y_inline=False, 
                         linestyle='--', color='k', linewidth=0.75)
        gl.top_labels = False
        gl.right_labels = False
        gl.bottom_labels = True
        gl.left_labels = True
        
        # Clean grid label styling
        gl.xlabel_style = {'fontsize': 12, 'fontweight': 'normal'}
        gl.ylabel_style = {'fontsize': 12, 'fontweight': 'normal'}
        
        # Standard padding for grid labels
        gl.xpadding = 10
        gl.ypadding = 10

    # Add a dedicated axis for the colorbar
    cbar_ax = fig.add_axes([0.15, 0.05, 0.7, 0.02])
    cbar = fig.colorbar(
        ScalarMappable(norm=norm, cmap=newcmap),
        cax=cbar_ax, orientation='horizontal', extend='max'
    )
    cbar.ax.tick_params(labelsize=16, labelrotation=0, width=1, length=5, direction='out')

    # Round colorbar tick labels to 1 decimal place
    ticks = cbar.get_ticks()
    cbar.ax.set_xticks(ticks)
    cbar.ax.set_xticklabels([f"{tick:.1f}" for tick in ticks])

    # Add title if suffix provided
    if title_suffix:
        fig.suptitle(f'GPCP Correction Ratios {title_suffix}', 
                    fontsize=20, fontweight='bold', y=0.95)

    # Adjust layout
    plt.tight_layout(rect=[0, 0.1, 1, 0.93 if title_suffix else 1])

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_monthly_comparison(data1, data2, labels=None, save_path=None):
    """
    Create a bar plot comparing monthly correction ratios from two methods.
    
    Parameters:
    -----------
    data1 : list or array
        First set of monthly correction ratios
    data2 : list or array
        Second set of monthly correction ratios
    labels : list, optional
        Labels for the two datasets
    save_path : str, optional
        Path to save the plot
        
    Returns:
    --------
    matplotlib.figure.Figure
        The created figure
    """
    if labels is None:
        labels = ['Method 1', 'Method 2']
    
    # Set up plotting parameters
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman'],
        'font.weight': 'bold',
        'axes.labelweight': 'bold',
        'axes.titleweight': 'bold',
        'xtick.labelsize': 18,
        'ytick.labelsize': 18,
        'axes.titlesize': 18,
        'axes.labelsize': 18
    })

    # Prepare data
    width = 0.4
    x = np.arange(1, 13)
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Create the bar plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width / 2, data1, width, label=labels[0], color='skyblue')
    ax.bar(x + width / 2, data2, width, label=labels[1], color='orange')

    # Customize plot
    ax.set_xticks(x)
    ax.set_xticklabels(month_names, fontsize=18, fontweight='bold')
    ax.set_xlabel('Month', fontsize=18, fontweight='bold')
    ax.set_ylabel('Correction Ratio', fontsize=18, fontweight='bold')
    ax.set_title('Monthly Correction Ratios Comparison', 
                fontsize=18, fontweight='bold')
    
    ax.grid(axis='y', alpha=0.3)
    ax.legend(fontsize=16, loc='upper right', frameon=True)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_single_method_bars(data, method_name="Method", save_path=None):
    """
    Create a bar plot for single method correction ratios.
    
    Parameters:
    -----------
    data : list or array
        Monthly correction ratios
    method_name : str
        Name of the method for the title
    save_path : str, optional
        Path to save the plot
        
    Returns:
    --------
    matplotlib.figure.Figure
        The created figure
    """
    # Set up plotting parameters
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman'],
        'font.weight': 'bold',
        'axes.labelweight': 'bold',
        'axes.titleweight': 'bold',
        'xtick.labelsize': 18,
        'ytick.labelsize': 18,
        'axes.titlesize': 18,
        'axes.labelsize': 18
    })

    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Create the bar plot
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(range(1, 13), data, color='skyblue', alpha=0.8)
    
    # Customize plot
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(month_names, fontsize=18, fontweight='bold')
    ax.set_xlabel('Month', fontsize=18, fontweight='bold')
    ax.set_ylabel('Correction Ratio', fontsize=18, fontweight='bold')
    ax.set_title(f'Monthly Correction Ratios - {method_name}', 
                fontsize=18, fontweight='bold')
    
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar, value in zip(bars, data):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{value:.2f}', ha='center', va='bottom', fontsize=12)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig
