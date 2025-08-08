"""
Basic usage example for Antarctica GPCP Precipitation Correction.

This script demonstrates how to use the GPCPCorrector class to compute
correction ratios for GPCP precipitation data over Antarctica.
"""

import os
import sys

# Add the package to Python path (for development)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from antarctica_precip_correction import GPCPCorrector


def main():
    """Run basic correction analysis."""
    
    # Define data paths (adjust these to your actual data locations)
    cs_data_path = "/ra1/pubdat/AVHRR_CloudSat_proj/CS_Antartica_analysis_kkk/CS-Antarctica_maps"
    gpcp_data_path = "/ra1/pubdat/Satellite_eval_over_Oceans/data/GPCP/GPCP_v3_pnt_3_monthly"
    mask_path = "/ra1/pubdat/mask_land_ocean/mask50km.mat"
    output_path = "./outputs"
    
    # Initialize the corrector
    print("Initializing GPCP Corrector...")
    corrector = GPCPCorrector(
        cs_data_path=cs_data_path,
        gpcp_data_path=gpcp_data_path,
        mask_path=mask_path,
        output_path=output_path
    )
    
    # Run the full analysis
    print("Running full analysis...")
    results = corrector.run_full_analysis(save_results=True, save_plots=True)
    
    # Print summary statistics
    print("\n" + "="*50)
    print("ANALYSIS RESULTS SUMMARY")
    print("="*50)
    
    print("\nDirect Method - Monthly Correction Ratios:")
    direct_single = results['direct_single']
    for _, row in direct_single.iterrows():
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        print(f"  {month_names[int(row['month'])-1]}: {row['crf']:.3f}")
    
    print(f"\nDirect Method - Average: {direct_single['crf'].mean():.3f}")
    
    print("\nReza's Method - Monthly Correction Ratios:")
    reza_single = results['reza_single']
    for _, row in reza_single.iterrows():
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        print(f"  {month_names[int(row['month'])-1]}: {row['crf']:.3f}")
    
    print(f"\nReza's Method - Average: {reza_single['crf'].mean():.3f}")
    
    print(f"\nResults saved to: {output_path}")
    print("Analysis complete!")


if __name__ == "__main__":
    main()
