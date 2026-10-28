SLIDERFORGE v1.2 — GITHUB RELEASES UPDATE CHECKER (BETA)

1. Create a GitHub repository, e.g. https://github.com/YOURNAME/SliderForge
2. Publish a GitHub Release tagged v1.2.1 (or higher), attaching a ZIP with 'SliderForge' in its filename.
3. In SliderForge, click 'Update Settings', enter YOURNAME/SliderForge, select stable or beta, Save.
4. Click 'Check for Updates'. If a newer release is found, approve the ZIP download.
5. The ZIP is downloaded to %USERPROFILE%\.sliderforge\downloads\ and checked for ZIP integrity.
6. Close the app, extract the new ZIP to a NEW folder, then run START_WINDOWS.bat.

This is a one-click update CHECK + DOWNLOAD, NOT unattended installation or in-place self-replacement.
The update checker never runs downloaded code. If GitHub supplies a SHA256 digest it is verified.
Only GitHub release ZIPs are accepted; keep your repository and release assets trusted.
The app does not modify %USERPROFILE%\.sliderforge\sliderforge.db during download.
Existing nine-game support is retained. Requires internet to check releases.
Older READMEs are historical; this file describes the current update behavior.
Python syntax tested, GUI and network not tested on Windows.
