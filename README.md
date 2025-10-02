CalibGuiPyQt
Installation
To set up the project locally, follow these steps:
1. Download the Repository

Download the code as a ZIP file from the GitHub repository.
Extract the ZIP to your desired directory.

2. Set Up the Conda Environment

Install Miniforge:

Download the Windows installer from Conda-Forge.
Check Installation Path: Default path is C:\Users\USERNAME\AppData\Local\miniforge3. Open Miniforge via Miniforge3 Prompt or run scripts\activate.bat in Command Prompt.
See Conda-Forge Setup for details.


Configure Conda Channel:

The .condarc file, created during Miniforge installation, specifies package sources. Use Infineon’s internal server for security.
Open Command Prompt as Administrator (Windows Key → type cmd → right-click → "Run as administrator").
Edit .condarc:notepad C:\Users\USERNAME\.condarc


Ensure it contains:channels:
  - https://artifactory.intra.infineon.com/artifactory/conda-it-conda-forge


Save and close.
Verify channel:conda config --show-sources

→ Should list only https://artifactory.intra.infineon.com/artifactory/conda-it-conda-forge.conda info

→ Confirm URLs: https://artifactory.intra.infineon.com/artifactory/conda-it-conda-forge/win-64 and noarch.
Troubleshooting:
If .condarc is missing, create it:echo default_channels: > %USERPROFILE%\.condarc
echo - https://artifactory.intra.infineon.com/artifactory/conda-it-conda-forge >> %USERPROFILE%\.condarc
type %USERPROFILE%\.condarc


If other channels (e.g., conda-forge) appear, remove them:del C:\path\to\other\.condarc






Create and Activate Environment:

In Miniforge Prompt or Command Prompt:conda create -n calibration_pyqt python=3.7
conda activate calibration_pyqt





3. Install Dependencies

Install PyQt and required packages:conda install pyqt
pip install pyqt5-tools
pip install numpy==1.16.4 pandas==0.24.2
pip install scipy==1.2.1 matplotlib==3.1.0 gwyfile==0.2.0
pip install pynverse==0.1.4.4
pip install openpyxl==2.6.2



Usage
1. Run the Application

With calibration_pyqt environment activated, navigate to project directory:cd path/to/CalibGuiPyQt
conda activate calibration_pyqt
python main.py


The GUI launches, enabling data import, measurement alignment, fit point selection, and calibration visualization.

File Structure
CalibGuiPyQt/
│
├── main.py                # Entry point for PyQt application
├── ui/                    # Qt Designer .ui files for GUI design
│    ├── main_window.ui    # Main window design file
├── generated_ui/          # Auto-generated Python files from .ui
│    ├── main_window.py    # Generated Python for main window
├── app/                   # Application logic and utilities
│    ├── import_measurement_tab.py  # Import measurement data logic
│    ├── select_calibration_tab.py # Calibration data selection logic
│    ├── alignment.py              # Alignment algorithms
│    ├── fitpoints.py              # Fit point selection logic
│    ├── calibration.py            # Calibration curve generation


main.py: Initializes and runs the PyQt app, loading GUI and connecting tabs.
ui/: Contains .ui files created with Qt Designer for GUI layout.
generated_ui/: Stores Python files generated from .ui using pyuic5.
app/: Modular scripts for core functionality (import, calibration, etc.).

Modifying the GUI with Qt Designer
To customize the GUI, edit main_window.ui using Qt Designer:
1. Open Qt Designer

Locate in Conda environment:C:\Users\USERNAME\.conda\envs\calibration_pyqt\Library\bin\designer.exe

Replace USERNAME with your Windows username.
Run designer.exe.

2. Edit the UI

Open ui/main_window.ui in Qt Designer.
Modify layout, add/remove widgets, or adjust properties (e.g., enabled, visible).
Save with Ctrl+S.

3. Generate Python Code

Convert updated .ui to Python:pyuic5 -x ui/main_window.ui -o generated_ui/main_window.py


Updates generated_ui/main_window.py.

4. Run the Application

Test changes:python main.py


