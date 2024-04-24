Project Title:      Virtual Paper Piano
Project Author:     Jess Aitken, Richard Green
Project Date:       24th May 2022

Project Description:
This application allows a user to play a virtual paper keyboard

How to Run:
1. Print off the file "keyboard.pdf" at normal size
2. Tape keyboard to desk ~80mm from front of laptop
3. Tilt laptop angle to ~45 degrees
4. Run initial reference frame capture from piano.py
    - comment out remainder of program past hough lines to ensure only two lines are present
    - adjust hough and canny parameters in merged_hough -> hough_merged_image until two horizontal lines
       at the top and bottom of the keyboard are present. Lines must go from corner to corner and only two
5. Comment out reference image timer
6. Run piano.py again
    - play the piano by pressing with either index finger on the keyboard


Areas for Improvement:
1. Robustness of Keyboard Detection:
    - Requires Hough parameters to be changed each time the camera angle or lighting changes
    - There can only be two horizontal lines for the keyboard base and top lines for the program to work

2. Main Function:
    - Before while loop is initial reference frame processing, could be done outside of main function 
    - Within while loop would need multiple flags to allow for multiple fingers to be pressed at once, as the order of left then right matters

3. Multiple Fingers:
    - Adding further processing to allow all fingertip locations to be detected
    - Within while loop would have to allow for multiple fingers to be pressed at once so multiple flags rather than just one

4. Computational Time:
    - decrease computational overload of system, starts to fail after around 45 seconds

5. Touch Detection Algorithm:
    - Increase robustness of algorithm so that touches aren't detected when they are stationary and above the paper
    - This will remove false positives and increase accuracy above 91.8%

6. Key Notes:
    - Currently have no piano notes for the first octave (notes 0-6 and 15-19), only for the second (notes 7-14 and 20-24)
    - Rather than multiple .wav files, use the switcher to set a certain frequency to be played
    - May allow for chords to be played which is not possible currently