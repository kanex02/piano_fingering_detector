Project Title:      Piano Fingering Detection System
Project Author:     Kane Xie, Richard Green
Project Date:       3rd May 2024

Project Description:
Tracks the fingering used by a user when playing a MIDI keyboard.

How to Run:
1. Place the camera such that it faces the user straight on, and has a clear view of the entirety of a 49-note MIDI
    keyboard (that is connected to the computer via USB)
2. Run find_camera_calibration.py and display checkerboard.png in a variety of locations to generate camera calibration
    data
3. Leave hands clear of the keyboard and run piano.py
4. When a video feed pops up, press any key on the typing keyboard to take a reference image
5. When the next video feed pops up, play keys on the MIDI keyboard for the system to record the fingering
6. To end the program and save the data to output.txt, press any key on the typing keyboard.


Areas for Improvement:
1. Speed - many custom algorithms are slow and inefficient, and could be greatly simplified
2. Robustness - every time lighting conditions change, Hough and Canny parameters need to be recalibrated
3. Accuracy - the program often (~10% of the time) fails to detect fingering if the user plays keys near the ends of the
    keyboard