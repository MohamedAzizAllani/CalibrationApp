```markdown
# CalibGuiPyQt



## Installation
To set up the project locally, follow these steps:

1. **Download the Repository**:
   - Download the code as a ZIP file from the GitHub repository.
   - Extract the ZIP file to your desired directory.

2. **Set Up the Conda Environment**:
   - Open a command prompt or terminal.
   - Create and activate a Conda environment with Python 3.7:
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
     ```

## Usage
1. **Run the Application**:
   - In the command prompt with the `calibration_pyqt` environment activated, navigate to the project directory:
     ```bash
     cd path/to/CalibGuiPyQt
     ```
   - Run the main script:
     ```bash
     python main.py
     ```
   - The GUI will launch, allowing you to import data, align measurements, select fit points, and visualize calibration results.

2. **Interacting with the GUI**:
   - Use the **Import Measurement Tab** to load measurement data.
   - Use the **Select Calibration Tab** to load calibration data.
   - Perform alignment in the **Alignment Tab** (automatic or manual modes).
   - Select fit points in the **Fitpoints Tab** and generate calibration curves in the **Calibration Tab**.

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
- **`ui/`**: Contains `.ui` files created with Qt Designer, defining the GUI layout.
- **`generated_ui/`**: Stores Python files generated from `.ui` files using `pyuic5`.
- **`app/`**: Contains modular Python scripts for the application's core functionality, including data import, alignment, fit point selection, and calibration.

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

**Note**: Ensure the `enabled` property is set to `True` for `QGroupBox` and its child widgets in Qt Designer to keep them interactable.

## Dependencies
The application requires the following Python packages with specific versions:
- `python==3.7`
- `pyqt`
- `pyqt5-tools`
- `numpy==1.16.4`
- `pandas==0.24.2`
- `scipy==1.2.1`
- `matplotlib==3.1.0`
- `gwyfile==0.2.0`
- `pynverse==0.1.4.4`
- `openpyxl==2.6.2`

These are installed via the commands in the [Installation](#installation) section.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
```

### Instructions
1. **Copy the Content**:
   - Copy the entire Markdown text above (from `# CalibGuiPyQt` to the end).
2. **Create README.md**:
   - In your `CalibGuiPyQt` repository root, create a file named `README.md`.
   - Paste the copied content into `README.md` and save.
3. **Upload to GitHub**:
   - Add and commit the file:
     ```bash
     git add README.md
     git commit -m "Add README file"
     git push origin main
     ```
   - Or, in GitHub's web interface:
     - Click "Add file" → "Create new file".
     - Name it `README.md`, paste the content, and commit.
4. **Verify**:
   - Visit your repository on GitHub to ensure the README renders with proper headings, code blocks, and formatting.

This single file is ready to use and includes all the requested design elements (headings, code blocks, lists) with default Markdown styling for clean rendering on GitHub.
