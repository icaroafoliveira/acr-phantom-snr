# CalculoSNR_ACR_test.py
# Description: Calculates the SNR as in the ACR quality assurance test.
# Author: Oliveira, IAF
# Date: 09-07-2025

# This script is designed to calculate the Signal-to-Noise Ratio (SNR) for a given DICOM or NIFTI (GZ) image.
# It reads a image file, extracts the pixel data, and computes the SNR based on the mean signal intensity and the standard deviation of the noise.
# The script also includes functionality to visualize the image and display the calculated SNR.

import nibabel
import os
import argparse
import pydicom
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt


def compute_snr(dataROIsignal, dataROInoise1, dataROInoise2):
    
    
    mean_signal = np.mean(dataROIsignal)
    std_noise = np.sqrt(np.mean((np.std(dataROInoise1, ddof=1))**2 + (np.std(dataROInoise2, ddof=1))**2))
    
    if std_noise == 0:
        return float('inf')  # Avoid division by zero
    
    snr = mean_signal / std_noise
    return snr

def load_image(file_path):
    if file_path.lower().endswith('.dcm'):
        ds = pydicom.dcmread(file_path)
        data = ds.pixel_array
    elif file_path.lower().endswith('.gz') or file_path.lower().endswith('.nii'):
        img = nib.load(file_path)
        data = img.get_fdata()
    else:
        raise ValueError("Unsupported file format. Please provide a DICOM or NIFTI (GZ) file.")
    
    return data

def create_ROIs(img_data):
    
    # Central ROI (roi signal)
    # Define ROIs based on the image data shape
    h, w = img_data.shape[:2]
    y, x = np.ogrid[:h, :w]
    center_x, center_y = w // 2, h // 2
    
    radius_mm = 95 * np.sqrt(0.75) # Radius for the ROI, adjusted as 75% of the area of a circle with diameter of 190mm
    
    # don't need to convert radius from mm to pixels, as the image has 1mm in-plane resolution
    mask_roi_signal = (x - center_x)**2 + (y - center_y)**2 <= radius_mm**2
    
    # Create noise ROIs
    # ROI 1: Top left
    height, width= 15, 160
    x_top, y_top = 48, 5
    mask_top = np.zeros((h, w), dtype=bool) #np.zeros_like([(h,w)])
    mask_top[y_top:y_top+height, x_top:x_top+width] = True
    
    # ROI 2: Bottom right
    x_bottom, y_bottom = 48, 236
    mask_bottom = np.zeros((h, w), dtype=bool) #np.zeros_like([(h,w)])
    mask_bottom[y_bottom:y_bottom+height, x_bottom:x_bottom+width] = True    
    
    return mask_roi_signal, mask_top, mask_bottom

def main():
    parser = argparse.ArgumentParser(description="Compute SNR from DICOM or NIFTI image.")
    parser.add_argument("file_path", type=str, help="Path to the DICOM or NIFTI (GZ) image file.")
    args = parser.parse_args()
    
    # Load the image
    img = load_image(args.file_path)
    
    # Check if the image is 3D and handle accordingly
    if img.ndim == 3:
        print("Image is 3D, using the slice 7 for SNR calculation.")
        img = img[:, :, 6]
        
    # Create ROIs for SNR calculation
    mask_roi_signal, mask_top, mask_bottom = create_ROIs(img)
    
    # values in the ROIs
    roi_signal = img[mask_roi_signal]
    roi_noise1 = img[mask_top]
    roi_noise2 = img[mask_bottom]
    
    # SNR calculation
    snr = compute_snr(roi_signal, roi_noise1, roi_noise2)
    print(f"Calculated SNR: {snr:.2f}")
    
    # Display the image and ROIs
    plt.figure(figsize=(10, 10))
    plt.imshow(img, cmap='gray')
    plt.contour(mask_roi_signal, colors='r', linewidths=1.5)
    plt.contour(mask_top, colors='g', linewidths=1.5)
    plt.contour(mask_bottom, colors='b', linewidths=1.5)
    plt.text(10, 100, f"Signal ROI\nMean: {np.mean(roi_signal):.3f}\nStd: {np.std(roi_signal, ddof=1):.3f}",
        color='red', fontsize=12, bbox=dict(facecolor='black', alpha=0.5))
    plt.text(10, 20, f"Top ROI\nMean: {np.mean(roi_noise1):.3f}\nStd: {np.std(roi_noise1, ddof=1):.3f}",
        color='green', fontsize=12, bbox=dict(facecolor='black', alpha=0.5))
    plt.text(10, 200, f"Bottom ROI\nMean: {np.mean(roi_noise2):.3f}\nStd: {np.std(roi_noise2, ddof=1):.3f}",
        color='blue', fontsize=12, bbox=dict(facecolor='black', alpha=0.5))
    plt.axis('off')
    plt.show()
    
    
if __name__ == "__main__":
    main()
        