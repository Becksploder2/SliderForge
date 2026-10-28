SLIDERFORGE 0.3 - CAPTURE CARD PROTOTYPE

1. Install Python 3 on Windows (enable Add Python to PATH).
2. Double-click INSTALL_CAPTURE.bat to install capture dependencies.
3. Optional OCR requires Tesseract OCR separately installed and accessible on PATH.
4. Double-click START_WINDOWS.bat.
5. Select game mode, save/career, season and HOME/AWAY teams.
6. Click Capture card / ratings. Select the correct capture device index and Connect.
7. Open the game's ratings screen; Capture screen / Try OCR.
8. Check and correct OVR, OFF, DEF for both teams, then Confirm & Save.

The capture card must expose a DirectShow camera/video capture device. Some cards need vendor software or an OBS virtual camera. Close apps that hold the device exclusively.
The OCR parser is EXPERIMENTAL; it may not recognize CFB 27 layout. It does not automatically track the game or save unconfirmed ratings.
Exhibition, Dynasty and RTG data are stored separately under %USERPROFILE%\.sliderforge.
The official ratings CSV is bundled for CFB 27 baseline data.
This application never modifies the console/game settings automatically.


v0.4: Capture buttons moved to top toolbar; fixed oversized preview hiding controls.


v0.5: Experimental matchup-based USER/CPU slider recommendations. Choose controlled HOME/AWAY team and difficulty; automatic recalculation on ratings changes and after confirmed OCR save. Auto-adjust toggle allows manual editing. These are heuristic recommendations, not EA-verified slider calibrations. Capture device 1 worked for the initial tester.
