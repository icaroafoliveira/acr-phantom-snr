# acr-phantom-snr

This script is designed to calculate the Signal-to-Noise Ratio (SNR) for a given DICOM or NIFTI (GZ) image. \
Three ROIs are created, one in the center of the image in the slice 7 of the ACR phantom, \
the other two are noise related ROIs, one at the top of the image, and the other at the bottom.

usage: 

```python CalculoSNR_ACR_test.py filepath
```
The three ROIs and their mean and standard deviation are depicted in the figure below.
![Phantom ACR](https://github.com/icaroafoliveira/acr-phantom-snr/blob/main/ACR_phantomROIs.png)
