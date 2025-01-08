# SHIMCOcamera
camera

Procedure for taking a picture (or 10)
(1) plug power supply into camera
(2) plug camera into computer
(3) turn on power supply
(4) open software
(5) Change settings (easy to do on the GUI) and click APPLY
(6) Go to processing tab and enable background subtraction + grab background if desired 
(7) Set # of Frames, Set Filesplit to 1, TURN ON SAVING! 
(8) Go back to camera settings and start acquisition

OptimizedGUIwithPIXIS_PICAM.py is a GUI which can be connected to a PIXIS camera to take pictures.  OptimizedQthreadGUI.py is a demonstration GUI which can randomly generate "images" for testing out the GUI functionality outside from the lab. 

The "visualizations" Jupyter Notebook, in the Image Analysis folder, contains several visualizations of Images taken by the Camera, some of which are works in progress.

The PIXIS_PICAM initialization file sets starting PIXIS camera parameters and imports necessary packages for working with it.

The archive contains scrapped previous ideas that we still may find useful.

LAST UPDATED 1/8/25
