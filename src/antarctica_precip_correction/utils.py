"""
Utility functions for Antarctica precipitation correction.
"""

import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.signal import convolve2d


def ds_swaplon(ds):
    """
    Swap longitude coordinates from [0,360] to [-180,180] and rename lat/lon.
    
    Parameters:
    -----------
    ds : xarray.Dataset or xarray.DataArray
        Input dataset with longitude coordinates
        
    Returns:
    --------
    ds : xarray.Dataset or xarray.DataArray
        Dataset with swapped longitude coordinates
    """
    if 'lon' in ds.coords:
        ds = ds.rename({'lon': 'longitude'})
    if 'lat' in ds.coords:
        ds = ds.rename({'lat': 'latitude'})
    ds = ds.assign_coords(longitude=(((ds.longitude + 180) % 360) - 180))
    return ds.sortby('longitude')


def apply_filter(array, method="convolution", sigma=1.4, kernel=None):
    """
    Apply spatial filtering to array data.
    
    Parameters:
    -----------
    array : numpy.ndarray
        Input array to filter
    method : str
        Filtering method ('gaussian' or 'convolution')
    sigma : float
        Standard deviation for Gaussian filter
    kernel : numpy.ndarray, optional
        Convolution kernel (default: 5x5 ones array)
        
    Returns:
    --------
    numpy.ndarray
        Filtered array
    """
    if kernel is None:
        kernel = np.ones((5, 5))
        
    if method == "gaussian":
        new_array = gaussian_filter(array, sigma=(sigma, sigma), order=0)
    elif method == "convolution":
        new_array = convolve2d(array, kernel, boundary="symm", mode="same")
        new_array = new_array / kernel.sum()
    else:
        raise ValueError(f"Unknown filtering method: {method}")

    return new_array


def apply_cap(array, cap=3):
    """
    Apply caps to correction ratios to prevent extreme values.
    
    Parameters:
    -----------
    array : numpy.ndarray
        Input correction ratio array
    cap : float
        Maximum cap value (minimum will be 1/cap)
        
    Returns:
    --------
    numpy.ndarray
        Capped array values
    """
    minimum = 1 / cap
    maximum = cap
    temp = np.where(array > maximum, maximum, array)
    temp = np.where(temp < minimum, minimum, temp)
    return temp


def get_zonal(spatial_product, mask, y, axis=(0, 1)):
    """
    Calculate area-weighted zonal average.
    
    Parameters:
    -----------
    spatial_product : numpy.ndarray
        Spatial data array
    mask : numpy.ndarray
        Land/ocean mask
    y : numpy.ndarray
        Latitude coordinates
    axis : tuple
        Axes to average over
        
    Returns:
    --------
    float
        Zonal average value
    """
    cosines = np.cos(np.radians(y))[:, np.newaxis]  # Broadcast to match mask shape
    cosines = np.where(mask, cosines, 0)
    weights = cosines / np.nansum(cosines)
    return np.nansum(weights * spatial_product, axis=axis)


def cf_calculator(reference, target, mask, quantile=1 - 1e-6):
    """
    Calculate correction factors using quantile-based method.
    
    Parameters:
    -----------
    reference : numpy.ndarray
        Reference precipitation data (CloudSat)
    target : numpy.ndarray
        Target precipitation data (GPCP)
    mask : numpy.ndarray
        Land mask
    quantile : float
        Quantile threshold for capping extreme values
        
    Returns:
    --------
    numpy.ndarray
        Correction factors
    """
    product_land = np.where(mask, target, np.nan)
    q99 = np.nanquantile(product_land, quantile)
    new_product = np.where(product_land > q99, q99, target)
    new_product = np.where(~mask, target, new_product)
    product_smoothed = apply_filter(new_product)
    
    return reference / product_smoothed


def cf_smoother(reference, target, cf, mask, y, cap=3, tolerance=1e-3, max_iterations=5):
    """
    Smooth correction factors using iterative zonal averaging.
    
    Parameters:
    -----------
    reference : numpy.ndarray
        Reference precipitation data
    target : numpy.ndarray
        Target precipitation data
    cf : numpy.ndarray
        Initial correction factors
    mask : numpy.ndarray
        Land mask
    y : numpy.ndarray
        Latitude coordinates
    cap : float
        Maximum cap value
    tolerance : float
        Convergence tolerance
    max_iterations : int
        Maximum number of iterations
        
    Returns:
    --------
    numpy.ndarray
        Smoothed correction factors
    """
    cf_capped = apply_cap(cf, cap)
    zonal_reference = get_zonal(reference, mask, y)
    zonal_product = get_zonal(target * cf_capped, mask, y)
    ratio = zonal_reference / zonal_product
    
    i = 1
    while (abs(1 - ratio) > tolerance) and (i < max_iterations):
        apply_conditional = (cf_capped <= cap) & (cf_capped >= 1 / cap)
        cf_capped = np.where(apply_conditional, cf_capped * ratio, cf_capped)
        zonal_product = get_zonal(target * cf_capped, mask, y)
        ratio = zonal_reference / zonal_product
        i += 1
    
    return cf_capped
