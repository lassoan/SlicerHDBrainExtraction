import logging
import os

import vtk

import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin


#
# HDBrainExtractionTool
#

class HDBrainExtractionTool(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "HD Brain Extraction Tool"
    self.parent.categories = ["Segmentation"]
    self.parent.dependencies = []
    self.parent.contributors = ["Andras Lasso (PerkLab, Queen's University)"]
    self.parent.helpText = """
Strip skull from brain MRI images using HD-BET tool.
See more information in <a href="https://github.com/lassoan/SlicerHDBrainExtraction">module documentation</a>.
"""
    self.parent.acknowledgementText = """
This file was originally developed by Andras Lasso (PerkLab, Queen's University).
The module uses <a href="https://github.com/MIC-DKFZ/HD-BET">HD-BET brain extraction toolkit</a>.
If you are using HD-BET, please cite the following publication: Isensee F, Schell M, Tursunova I, Brugnara G,
Bonekamp D, Neuberger U, Wick A, Schlemmer HP, Heiland S, Wick W, Bendszus M, Maier-Hein KH, Kickingereder P.
Automated brain extraction of multi-sequence MRI using artificial neural networks. Hum Brain Mapp. 2019; 1–13.
https://doi.org/10.1002/hbm.24750
"""

#
# HDBrainExtractionToolWidget
#

class HDBrainExtractionToolWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None
    self._parameterNode = None
    self._updatingGUIFromParameterNode = False

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/HDBrainExtractionTool.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create logic class. Logic implements all computations that should be possible to run
    # in batch mode, without a graphical user interface.
    self.logic = HDBrainExtractionToolLogic()

    # Connections

    # These connections ensure that we update parameter node when scene is closed
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

    # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
    # (in the selected parameter node).
    self.ui.inputVolumeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.outputVolumeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.outputSegmentationSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.deviceComboBox.connect("currentIndexChanged(int)", self.updateParameterNodeFromGUI)

    # Buttons
    self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)

    # Make sure parameter node is initialized (needed for module reload)
    self.initializeParameterNode()

  def cleanup(self):
    """
    Called when the application closes and the module widget is destroyed.
    """
    self.removeObservers()

  def enter(self):
    """
    Called each time the user opens this module.
    """
    # Make sure parameter node exists and observed
    self.initializeParameterNode()

  def exit(self):
    """
    Called each time the user opens a different module.
    """
    # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
    self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

  def onSceneStartClose(self, caller, event):
    """
    Called just before the scene is closed.
    """
    # Parameter node will be reset, do not use it anymore
    self.setParameterNode(None)

  def onSceneEndClose(self, caller, event):
    """
    Called just after the scene is closed.
    """
    # If this module is shown while the scene is closed then recreate a new parameter node immediately
    if self.parent.isEntered:
      self.initializeParameterNode()

  def initializeParameterNode(self):
    """
    Ensure parameter node exists and observed.
    """
    # Parameter node stores all user choices in parameter values, node selections, etc.
    # so that when the scene is saved and reloaded, these settings are restored.

    self.setParameterNode(self.logic.getParameterNode())

    # Select default input nodes if nothing is selected yet to save a few clicks for the user
    if not self._parameterNode.GetNodeReference("InputVolume"):
      firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
      if firstVolumeNode:
        self._parameterNode.SetNodeReferenceID("InputVolume", firstVolumeNode.GetID())

  def setParameterNode(self, inputParameterNode):
    """
    Set and observe parameter node.
    Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
    """

    if inputParameterNode:
      self.logic.setDefaultParameters(inputParameterNode)

    # Unobserve previously selected parameter node and add an observer to the newly selected.
    # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
    # those are reflected immediately in the GUI.
    if self._parameterNode is not None:
      self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
    self._parameterNode = inputParameterNode
    if self._parameterNode is not None:
      self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    # Initial GUI update
    self.updateGUIFromParameterNode()

  def updateGUIFromParameterNode(self, caller=None, event=None):
    """
    This method is called whenever parameter node is changed.
    The module GUI is updated to show the current state of the parameter node.
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
    self._updatingGUIFromParameterNode = True

    # Update node selectors and sliders
    self.ui.inputVolumeSelector.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume"))
    self.ui.outputVolumeSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolume"))
    self.ui.outputSegmentationSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputSegmentation"))
    self.ui.deviceComboBox.setCurrentText(self._parameterNode.GetParameter("Device"))

    # Update buttons states and tooltips
    inputVolume = self._parameterNode.GetNodeReference("InputVolume")
    if inputVolume and (self._parameterNode.GetNodeReference("OutputVolume") or self._parameterNode.GetNodeReference("OutputSegmentation")):
      self.ui.applyButton.toolTip = "Extract brain"
      self.ui.applyButton.enabled = True
    else:
      self.ui.applyButton.toolTip = "Select input volume and at least one output"
      self.ui.applyButton.enabled = False

    if inputVolume:
      self.ui.outputVolumeSelector.baseName = inputVolume.GetName() + " stripped"
      self.ui.outputSegmentationSelector.baseName = inputVolume.GetName() + " mask"

    # All the GUI updates are done
    self._updatingGUIFromParameterNode = False

  def updateParameterNodeFromGUI(self, caller=None, event=None):
    """
    This method is called when the user makes any change in the GUI.
    The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

    self._parameterNode.SetNodeReferenceID("InputVolume", self.ui.inputVolumeSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("OutputVolume", self.ui.outputVolumeSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("OutputSegmentation", self.ui.outputSegmentationSelector.currentNodeID)
    self._parameterNode.SetParameter("Device", self.ui.deviceComboBox.currentText)

    self._parameterNode.EndModify(wasModified)

  def onApplyButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
    with slicer.util.tryWithErrorDisplay("Failed to compute results.", waitCursor=True):

      self.logic.setupPythonRequirements()

      if self.ui.deviceComboBox.currentIndex == 0:
        device = "auto"
      elif self.ui.deviceComboBox.currentIndex == 1:
        device = "cpu"
      else:
        device = (self.ui.deviceComboBox.currentIndex - 2)

      # Compute output
      self.logic.process(self.ui.inputVolumeSelector.currentNode(), self.ui.outputVolumeSelector.currentNode(),
        self.ui.outputSegmentationSelector.currentNode(), device)

      if self.ui.outputVolumeSelector.currentNode():
        slicer.util.setSliceViewerLayers(background=self.ui.outputVolumeSelector.currentNode())

#
# HDBrainExtractionToolLogic
#

class HDBrainExtractionToolLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)

  def setupPythonRequirements(self):

    # Install PyTorch
    import PyTorchUtils
    torchLogic = PyTorchUtils.PyTorchUtilsLogic()
    if not torchLogic.torchInstalled():
      logging.info('PyTorch module not found')
      torch = torchLogic.installTorch(askConfirmation=True)
      if torch is None:
        raise ValueError('PyTorch extension needs to be installed to use this module.')

    # Install HD-BET
    needToInstallHdBet = False
    try:
      import HD_BET
    except ModuleNotFoundError as e:
      needToInstallHdBet = True
    if needToInstallHdBet:
      # Download HD-BET repository from github as a zip file
      tempFolder = slicer.util.tempDirectory()
      import SampleData
      dataLogic = SampleData.SampleDataLogic()
      ref = "0dcab33233e991b9f7a7cb33052b164eb50062bd"  # v1.1
      hdBetZipFilePath = dataLogic.downloadFile(f'https://github.com/MIC-DKFZ/HD-BET/archive/{ref}.zip', tempFolder, 'HD-BET.zip')
      # Unzip file
      slicer.util.extractArchive(hdBetZipFilePath, tempFolder)
      # Copy HD_BET subfolder to this module's folder so that it can be found as a Python package
      import shutil
      import os
      scriptedModulesPath = os.path.dirname(slicer.util.modulePath(self.moduleName))
      shutil.move(tempFolder + f"/HD-BET-{ref}/HD_BET", scriptedModulesPath+"/HD_BET")
      import HD_BET

    # Ensure that the download folder for model files exist
    import os
    import HD_BET.paths
    os.makedirs(HD_BET.paths.folder_with_parameter_files, exist_ok=True)

    # Install batchgenerators
    needToInstallBatchGenerators = False
    try:
      import batchgenerators
    except ModuleNotFoundError as e:
      needToInstallBatchGenerators = True
    if needToInstallBatchGenerators:
      slicer.util.pip_install('batchgenerators')

  def setDefaultParameters(self, parameterNode):
    """
    Initialize parameter node with default settings.
    """
    if not parameterNode.GetParameter("Device"):
      parameterNode.SetParameter("Device", "auto")

  def process(self, inputVolume, outputVolume, outputSegmentation, device=None):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    :param inputVolume: volume to be thresholded
    :param outputVolume: thresholding result
    :param imageThreshold: values above/below this threshold will be set to 0
    :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
    :param showResult: show output volume in slice viewers
    """

    if not inputVolume:
      raise ValueError("Input or output volume is invalid")

    import time
    startTime = time.time()
    logging.info('Processing started')

    if not device:
      device = "auto"

    if device == "auto":
      import PyTorchUtils
      torchLogic = PyTorchUtils.PyTorchUtilsLogic()
      if torchLogic.cuda:
        device = 0
      else:
        device = "cpu"

    import os
    from HD_BET.run import run_hd_bet
    from HD_BET.utils import maybe_mkdir_p, subfiles
    import HD_BET

    # Create new empty folder
    tempFolder = slicer.util.tempDirectory()

    input_file = tempFolder+"/hdbet-input.nii.gz"
    output_file = tempFolder+"/hdbet-output.nii.gz"
    output_segmentation_file = tempFolder+"/hdbet-output_mask.nii.gz"

    # Write input volume to file
    volumeStorageNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLVolumeArchetypeStorageNode")
    volumeStorageNode.SetFileName(input_file)
    volumeStorageNode.WriteData(inputVolume)
    volumeStorageNode.UnRegister(None)

    # Run the algorithm. This section is based on HD_BET\hd-bet script.
    # The mode='fast' and tta=False will disable test time data augmentation (speedup of 8x)
    # and use only one model instead of an ensemble of five models for the prediction,
    # to reduce computation time when no GPU is available (can still take 5-10 minutes).
    if device != 'cpu':
      # GPU is available
      mode = 'accurate'
      enable_augmentation = True
    else:
      # GPU is not available, only do fast, less accurate processing
      mode = 'fast'
      enable_augmentation = False
    save_mask = outputSegmentation is not None
    save_masked_volume = outputVolume is not None
    params_file = os.path.join(HD_BET.__path__[0], "model_final.py")
    config_file = os.path.join(HD_BET.__path__[0], "config.py")
    run_hd_bet([input_file], [output_file], mode, config_file, device, postprocess = True, do_tta = enable_augmentation, keep_mask = save_mask, overwrite = True, bet = save_masked_volume)

    # Input file is no longer needed
    os.remove(input_file)

    # Read results from output files

    if outputVolume:
      volumeStorageNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLVolumeArchetypeStorageNode")
      volumeStorageNode.SetFileName(output_file)
      volumeStorageNode.ReadData(outputVolume)
      volumeStorageNode.UnRegister(None)
      os.remove(output_file)

    if outputSegmentation:
      segmentationStorageNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLSegmentationStorageNode")
      segmentationStorageNode.SetFileName(output_segmentation_file)
      segmentationStorageNode.ReadData(outputSegmentation)
      segmentationStorageNode.UnRegister(None)
      os.remove(output_segmentation_file)

      # Set segment terminology
      segmentId = outputSegmentation.GetSegmentation().GetNthSegmentID(0)
      segment = outputSegmentation.GetSegmentation().GetSegment(segmentId)
      segment.SetTag(segment.GetTerminologyEntryTagName(),
        "Segmentation category and type - 3D Slicer General Anatomy list"
        "~SCT^123037004^Anatomical Structure"
        "~SCT^12738006^Brain"
        "~^^"
        "~Anatomic codes - DICOM master list"
        "~^^"
        "~^^")
      segment.SetName("brain")
      segment.SetColor(0.9803921568627451, 0.9803921568627451, 0.8823529411764706)

    stopTime = time.time()
    logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')


#
# HDBrainExtractionToolTest
#

class HDBrainExtractionToolTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear()

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_HDBrainExtractionTool1()

  def test_HDBrainExtractionTool1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")

    # Get/create input data

    import SampleData
    inputVolume = SampleData.downloadSample('MRBrainTumor1')
    self.delayDisplay('Loaded test data set')

    outputVolume = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLScalarVolumeNode')
    outputSegmentation = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLSegmentationNode')

    # Test the module logic

    # Logic testing is disabled by default to not overload automatic build machines (pytorch is a huge package and computation
    # on CPU takes 5-10 minutes). Set testLogic to True to enable testing.
    testLogic = False

    if testLogic:
      logic = HDBrainExtractionToolLogic()

      self.delayDisplay('Set up required Python packages')
      logic.setupPythonRequirements()

      self.delayDisplay('Compute output')
      logic.process(inputVolume, outputVolume, outputSegmentation)

      slicer.util.setSliceViewerLayers(background=outputVolume)

    else:
      logging.warning("test_HDBrainExtractionTool1 logic testing was skipped")

    self.delayDisplay('Test passed')
