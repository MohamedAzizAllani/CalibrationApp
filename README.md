# CalibGuiPyQt

## Installation
To set up the project locally, follow these steps:

1. **Download the Repository**:
   - Download the code as a ZIP file from the GitHub repository.
   - Extract the ZIP file to your desired directory.

Réponse A

Réflexion pendant 12s
markdown
### 2. Set Up the Conda Environment
- **Install Miniforge**:
  - Download the Windows installer for Miniforge from [https://conda-forge.org/download/](https://conda-forge.org/download/).
  - **Check Installation Path**: If you didn't change the default path, Miniforge installs to `C:\Users\USERNAME\AppData\Local\miniforge3`. To open Miniforge, navigate to this folder and run `Miniforge3 Prompt` or `scripts\activate.bat` in Command Prompt.
  - For detailed guidance, refer to [Conda-Forge Setup](https://confluencewikiprod.intra.infineon.com/spaces/ANACONDA/pages/1813645274/Conda-Forge).

- **Set Up the Conda Channel**:
  - The `.condarc` file, created during Miniforge installation or by running `conda config`, specifies where Conda downloads packages. Use Infineon's internal server for security.
  - Open Command Prompt as Administrator (Windows Key → type `cmd` → right-click → "Run as administrator").
  - Open `.condarc`:
notepad C:\Users\USERNAME.condarc


- Ensure it contains only:
  
channels:
https://artifactory.intra.infineon.com/artifactory/conda-it-conda-forge


- Save and close Notepad.
- Verify the channel:
conda config --show-sources


→ Check it lists only `https://artifactory.intra.infineon.com/artifactory/conda-it-conda-forge`.
conda info

text
→ Confirm channel URLs are `https://artifactory.intra.infineon.com/artifactory/conda-it-conda-forge/win-64` and `noarch`.
- **Troubleshooting**:
- If `.condarc` is missing, create it:
  ```bash
  echo default_channels: > C:\Users\USERNAME\AppData\Local\miniforge3\.condarc
  echo - https://artifactory.intra.infineon.com/artifactory/conda-it-conda-forge >> C:\Users\USERNAME\AppData\Local\miniforge3\.condarc
  type C:\Users\USERNAME\AppData\Local\miniforge3\.condarc
If other channels appear (e.g., conda-forge), remove them:
bash
del C:\path\to\other\.condarc
Create and Activate Environment:
Open Miniforge Prompt or Command Prompt.
Create and activate a Conda environment with Python 3.7:
bash
conda create -n calibration_pyqt python=3.7
conda activate calibration_pyqt
Ajouter au chat


3. **Install Dependencies**:
   - Install PyQt and required packages:
     ```bash
     conda install pyqt
     pip install pyqt5-tools
     pip install numpy==1.16.4 pandas==0.24.2
     pip install scipy==1.2.1 matplotlib==3.1.0 gwyfile==0.2.0
     pip install pynverse==0.1.4.4
     pip install openpyxl==2.6.2
     ```

## Usage
1. **Run the Application**:
   - In the command prompt with the `calibration_pyqt` environment activated, navigate to the project directory:
     ```bash
     cd path/to/CalibGuiPyQt
     ```
   - Run the main script:
     ```bash
     conda activate calibration_pyqt
     ```     
   - Run the main script:
     ```bash
     python main.py
     ```
   - The GUI will launch, allowing you to import data, align measurements, select fit points, and visualize calibration results.



## File Structure
The repository is organized as follows:

```
CalibGuiPyQt/
│
├── main.py                # Entry point for launching the PyQt application
├── ui/                    # Qt Designer .ui files for the GUI design
│    ├── main_window.ui    # Main window design file
├── generated_ui/          # Auto-generated Python files from .ui files
│    ├── main_window.py    # Generated Python code for the main window
├── app/                   # Application logic and utilities
│    ├── import_measurement_tab.py  # Logic for importing measurement data
│    ├── select_calibration_tab.py # Logic for selecting calibration data
│    ├── alignment.py              # Alignment algorithms and logic
│    ├── fitpoints.py              # Fit point selection logic
│    ├── calibration.py            # Calibration curve generation logic
```

- **`main.py`**: The main script that initializes and runs the PyQt application, loading the GUI and connecting all tabs.
- **`ui/`**: Contains `.ui` file created with Qt Designer, defining the GUI layout.
- **`generated_ui/`**: Stores Python file generated from `.ui` file using `pyuic5`.
- **`app/`**: Contains modular Python scripts for the application's core functionality(import measurement tab ...)

## Modifying the GUI with Qt Designer
To customize the GUI, you can edit the `main_window.ui` file using Qt Designer:

1. **Open Qt Designer**:
   - Locate Qt Designer in your Conda environment:
     ```
     C:\Users\USERNAME\.conda\envs\calibration_pyqt\Library\bin\designer.exe
     ```
     Replace `USERNAME` with your Windows username.
   - Run `designer.exe` to open Qt Designer.

2. **Edit the UI**:
   - Open `ui/main_window.ui` in Qt Designer.
   - Modify the GUI layout, add/remove widgets, or adjust properties (e.g., `enabled`, `visible`).
   - Save changes by pressing `Ctrl+S`.

3. **Generate Python Code**:
   - After modifying `main_window.ui`, convert it to Python code:
     ```bash
     pyuic5 -x ui/main_window.ui -o generated_ui/main_window.py
     ```
   - This updates `generated_ui/main_window.py` with your changes.

4. **Run the Application**:
   - Run `python main.py` to test the modified GUI.





