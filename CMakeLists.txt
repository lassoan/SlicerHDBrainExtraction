cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(HDBrainExtraction)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/lassoan/SlicerHDBrainExtraction")
set(EXTENSION_CATEGORY "Segmentation")
set(EXTENSION_CONTRIBUTORS "Andras Lasso (PerkLab, Queen's University)")
set(EXTENSION_DESCRIPTION "Strip skull in brain MRI images using HD-BET brain extraction tool. HD-BET was developed with MRI-data from a large multicentric clinical trial in adult brain tumor patients acquired across 37 institutions in Europe and included a broad range of MR hardware and acquisition parameters, pathologies or treatment-induced tissue alterations. HD-BET was trained with precontrast T1-w, postcontrast T1-w, T2-w and FLAIR sequences. It can perform independent brain extraction on various different MRI sequences and is not restricted to precontrast T1-weighted (T1-w) sequences. Other MRI sequences may work as well (just give it a try!) HD-BET was designed to be robust with respect to brain tumors, lesions and resection cavities as well as different MRI scanner hardware and acquisition parameters.")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/lassoan/SlicerHDBrainExtraction/main/HDBrainExtraction.png")
set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/lassoan/SlicerHDBrainExtraction/main/Screenshot01.jpg")
set(EXTENSION_DEPENDS "PyTorch")

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(HDBrainExtractionTool)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
