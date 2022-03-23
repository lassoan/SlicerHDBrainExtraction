cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(HDBrainExtraction)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/HDBrainExtraction")
set(EXTENSION_CATEGORY "Segmentation")
set(EXTENSION_CONTRIBUTORS "Andras Lasso (PerkLab, Queen's University)")
set(EXTENSION_DESCRIPTION "Strip skull in brain MRI images using HD-BET brain extraction tool. HD-BET was developed with MRI-data from a large multicentric clinical trial in adult brain tumor patients acquired across 37 institutions in Europe and included a broad range of MR hardware and acquisition parameters, pathologies or treatment-induced tissue alterations. HD-BET was trained with precontrast T1-w, postcontrast T1-w, T2-w and FLAIR sequences. It can perform independent brain extraction on various different MRI sequences and is not restricted to precontrast T1-weighted (T1-w) sequences. Other MRI sequences may work as well (just give it a try!)
HD-BET was designed to be robust with respect to brain tumors, lesions and resection cavities as well as different MRI scanner hardware and acquisition parameters.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/HDBrainExtraction.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/HDBrainExtraction/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

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
