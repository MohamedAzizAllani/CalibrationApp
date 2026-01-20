# CalibGuiPyQt

## Installation
To set up the project locally, follow these steps:

1. **Download the Repository**:
   - Download the code as a ZIP file from the GitHub repository.
   - Extract the ZIP file to your desired directory.


### 2. Set Up the Conda Environment
- **Install Miniforge**:
  - Download the Windows installer for Miniforge from [https://conda-forge.org/download/](https://conda-forge.org/download/).
  -  - **Important**: Add Miniforge to the PATH Environment Variable
   
     <img width="456" height="273" alt="Image" src="https://github.com/user-attachments/assets/17b306fd-c64e-4578-86a5-fedc19bdea5e" />
     
  - **Check Installation Path**: If you didn't change the default path, Miniforge installs to `C:\Users\USERNAME\AppData\Local\miniforge3`.

 

- **Set Up the Conda Channel**:
  - The `.condarc` file, created during Miniforge installation , specifies where Conda downloads packages. Use Infineon's internal server for security.
  - Open Command Prompt as Administrator (Windows Key → type `cmd` → right-click → "Run as administrator").
  - Open `.condarc`:
   ```bash
   notepad C:\Users\USERNAME\AppData\Local\miniforge3\.condarc


- Ensure it contains only:

   ```bash
   channels:
  - https://artifactory.intra.infineon.com/artifactory/conda-it-conda-forge



- Save and close Notepad.
  
- Verify the channel:
conda config --show-sources

→ Check it lists only `https://artifactory.intra.infineon.com/artifactory/conda-it-conda-forge`.

conda info


→ Confirm channel URLs are `https://artifactory.intra.infineon.com/artifactory/conda-it-conda-forge/win-64` and `noarch`.

- Create and Activate Environment:
Open Miniforge Prompt or Command Prompt.

```bash
conda create -n calibration_pyqt python=3.7
conda activate calibration_pyqt

```

3. **Install Dependencies**:
   - Install PyQt and required packages:
     ```bash
     conda install pyqt
     pip install pyqt5-tools
     pip install numpy==1.16.4 pandas==0.24.2
     pip install scipy==1.2.1 matplotlib==3.1.0 gwyfile==0.2.0
     pip install pynverse==0.1.4.4
     pip install openpyxl==2.6.2
     pip install pymongo
     ```
### 3. Set Up Local MongoDB Database

1. **Install MongoDB Community Server**  
   - Download the Windows MSI installer from:  
     https://www.mongodb.com/try/download/community  
   - Run the installer
<img width="300" height="273" alt="Step 1" src="https://github.com/user-attachments/assets/a7ef2545-d56c-4c28-a2d3-6a8cc65a2d0d" />
<img width="300" height="273" alt="Step 2" src="https://github.com/user-attachments/assets/1cc16977-91a3-442a-b384-804c37b7c092" />
<img width="300" height="273" alt="Step 3" src="https://github.com/user-attachments/assets/e7543862-ac16-498e-b6f3-28debd817a57" />
     

2. **Add MongoDB to PATH** (if not automatic)  
   - Search "Environment Variables" in Windows Start menu.  
   - Edit "Path" under **User variables**.  
   - Add: `C:\Program Files\MongoDB\Server\8.2\bin` (adjust version if different).  
   - OK → OK → restart terminal.
     
     <img width="456" height="273" alt="Image" src="https://github.com/user-attachments/assets/46e2be2d-a1bf-4f18-ae8f-c35c745b65e3" />

3. **Start the MongoDB Server**  
   Open a terminal/command prompt and run:
    ```bash
     mongod
     ```

4. **Use MongoDB Compass GUI**  
- Open Compass → Connect with:  
  `mongodb://localhost:27017`  
- View database: `calibration_db` → `calibrations` collection.

<img width="300" height="273"  alt="Step 2" src="[https://github.com/user-attachments/assets/e7543862-ac16-498e-b6f3-28debd817a57](https://github.com/user-attachments/assets/ebcbb12a-3879-444d-96dd-ecee57861688)" />
<img width="300" height="273"  alt="Step 1" src="https://github.com/user-attachments/assets/73964afb-4e64-40c6-bed4-18ed751e132d" />

 Restart your computer if PATH changes don't apply immediately.




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
     Comment from Thomas: For me it was 
     ```
     C:\Users\USERNAME\AppData\Local\miniforge3\envs\calibration
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





