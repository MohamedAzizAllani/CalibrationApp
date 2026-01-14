# import_parameters.py

import os
import json
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QMessageBox, QLineEdit, QWidget
)
from PyQt5.QtCore import Qt

class ImportParametersDialog(QDialog):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.setWindowTitle("Import Parameters")
        self.setMinimumSize(1150, 500)

        self.project_dir = os.path.expanduser("~/AppName/saved_projects")
        os.makedirs(self.project_dir, exist_ok=True)

        layout = QVBoxLayout()

        # Search
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by name / date / path / sample...")
        self.search_edit.textChanged.connect(self.filter_table)
        search_layout.addWidget(QLabel("Filter:"))
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)

        # Table (5 columns now)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "Project Name", "Date", "Measurement File", "Calibration Sample", "Actions"
        ])
        
        # All columns fixed narrow width + no stretch
        for col in range(5):
            self.table.setColumnWidth(col, 180)  # same width for all
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)  # lock all widths
        
        # Special for Measurement File (col 2): allow horizontal scroll
        self.table.setColumnWidth(2, 180)  # narrow
        self.table.setWordWrap(False)
        self.table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)


        # Refresh button
        #btn_layout = QHBoxLayout()
        #refresh_btn = QPushButton("Refresh List")
        #refresh_btn.clicked.connect(self.load_projects)
        #btn_layout.addWidget(refresh_btn)
        #layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.load_projects()

    def load_projects(self):
        self.table.setRowCount(0)

        for filename in sorted(os.listdir(self.project_dir), reverse=True):
            if not filename.endswith(".json"):
                continue
            path = os.path.join(self.project_dir, filename)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                row = self.table.rowCount()
                self.table.insertRow(row)

                # Project Name
                name_item = QTableWidgetItem(filename.replace(".json", ""))
                name_item.setData(Qt.UserRole, path)
                self.table.setItem(row, 0, name_item)

                # Date
                self.table.setItem(row, 1, QTableWidgetItem(data.get("project_saved_at", "—")))

                # Measurement Path
                meas_path = data.get("import_measurement", {}).get("measurement_file", "—")
                item = QTableWidgetItem(meas_path)
                item.setToolTip(meas_path)  # full path on hover
                self.table.setItem(row, 2, item)
                

                # Calibration Sample
                sample = data.get("select_calibration", {}).get("Calibration sample", "—")
                self.table.setItem(row, 3, QTableWidgetItem(sample))

                # Actions
                action_widget = QWidget()
                hbox = QHBoxLayout(action_widget)
                hbox.setContentsMargins(0, 0, 0, 0)

                load_btn = QPushButton("Load")
                load_btn.setStyleSheet("background-color: #4CAF50; color: white;")
                load_btn.clicked.connect(lambda _, p=path: self.import_parameters(p))

                del_btn = QPushButton("Delete")
                del_btn.setStyleSheet("background-color: #f44336; color: white;")
                del_btn.clicked.connect(lambda _, r=row, p=path: self.delete_project(r, p))

                hbox.addWidget(load_btn)
                hbox.addWidget(del_btn)
                self.table.setCellWidget(row, 4, action_widget)  # Column 4 = Actions

            except:
                continue

        self.table.resizeColumnsToContents()

    def filter_table(self, text):
        text = text.lower()
        for row in range(self.table.rowCount()):
            visible = any(
                text in (self.table.item(row, col).text() or "").lower()
                for col in range(4)  # Search in first 4 columns
            )
            self.table.setRowHidden(row, not visible)

    def import_parameters(self, path):
        # Same as before – no change needed here
        if not self.main_window.import_measurement_tab.X_data.size > 0:
            QMessageBox.warning(self, "No Data Loaded", 
                                "Please load a measurement file first.")
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            meas = self.main_window.import_measurement_tab
            calib = self.main_window.select_calibration_tab
            align = self.main_window.alignment_tab
            fit = self.main_window.fitpoints_tab

            # Import Measurement
            imp = settings.get("import_measurement", {})
            meas.ui.dataTypeComboBox.setCurrentText(imp.get("data_type", "SSRM"))
            meas.ui.denominationLineEdit.setText(imp.get("denomination", ""))
            meas.ui.flipDataCheckBox.setChecked(imp.get("flip_data", False))
            meas.borders_data = [imp.get("left_border_um", 0), imp.get("right_border_um", 0)]
            meas.original_borders_data = meas.borders_data[:]
            meas.data_is_flipped = imp.get("flip_data", False)
            meas.ui.flipDataCheckBox.setChecked(meas.data_is_flipped)
            meas.reset_data_window()
            self.main_window.import_measurement_tab.ui.applyParametersButton.click()

            # Select Calibration
            cal = settings.get("select_calibration", {})
            sample = cal.get("Calibration sample", "pcal")
            calib.ui.calib_sample_combobox.setCurrentText(sample)
            calib.update_calibration_sample(sample)

            preset = cal.get("preset", "")
            if preset and not calib.ui.Preset_comboBox.isHidden():
                calib.ui.Preset_comboBox.setCurrentText(preset)
                calib.update_preset_from_combo(preset)

            calib.ui.Flip_Data_Checkbox.setChecked(cal.get("flip_calibration", False))
            calib.ui.RawData_LinearScale_checkBox.setChecked(cal.get("linear_scale", False))
            calib.ui.Dopant_Type_comboBox.setCurrentText(cal.get("dopant_type", "B"))
            calib.ui.Nb_steps_spinBox.setValue(cal.get("number_of_steps", 5))
            calib.ui.Min_Step_LineEdit.setText(str(cal.get("min_step_distance", 0.3)))
            calib.borders_data = [cal.get("left_border_um", 0), cal.get("right_border_um", 0)]
            calib.original_borders_data = calib.borders_data[:]
            calib.data_is_flipped = cal.get("flip_calibration", False)
            calib.reset_data_window()
            self.main_window.select_calibration_tab.ui.apply_parameters_calib_tab_Button.click()

            # Alignment
            alg = settings.get("alignment", {})
            align.ui.DataFilterStrenght_slider.setValue(alg.get("filter_strength", 3))
            align.ui.FilterOrder_Slider.setValue(alg.get("filter_order", 1))
            align.ui.minStretch_slider.setValue(alg.get("min_stretch", -5))
            align.ui.MaxStretch_slider.setValue(alg.get("max_stretch", 5))
            align.ui.Increase_Search_area_checkbox.setChecked(alg.get("increase_search_area", False))
            align.ui.Search_resol_shift_lineedit.setText(str(alg.get("shift_resolution", "1000")))
            align.ui.Search_resol_Stretch_lineedit.setText(str(alg.get("stretch_resolution", "1000")))
            align.ui.fine_alignement_lineedit.setText(str(alg.get("fine-alignment_number_of_evaluated_points", "50")))
            self.main_window.alignment_tab.ui.Import_Calib_button.click()
            self.main_window.alignment_tab.ui.Import_Data_button.click()
            self.main_window.alignment_tab.ui.start_alignment_button.click()

            # Fitpoints
            fp = settings.get("fitpoints", {})
            mode = fp.get("mode", "Find fitpoints automatically")
            if "Manually" in mode:
                fit.set_manual_mode()
            else:
                fit.set_auto_mode()
            self.main_window.fitpoints_tab.ui.Fit_go_pushButton.click()

            fit.ui.Nbr_of_points_spinBox.setValue(fp.get("number_of_points", 5))
            fit.ui.Min_distance_between_steps_lineEdit.setText(str(fp.get("min_distance", 1.0)))
            fit.ui.include_left_edge_as_anchor_checkBox.setChecked(fp.get("include_left_edge", False))
            fit.ui.include_right_edge_as_anchor_checkBox.setChecked(fp.get("include_right_edge", False))

            intermediates = fp.get("intermediate_points", [0]*9)
            for i, val in enumerate(intermediates[:len(fit.sliders)]):
                fit.sliders[i].setValue(val)

            #QMessageBox.information(self, "Success", "Parameters imported.")
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Import failed:\n{e}")

    def delete_project(self, row, path):
        reply = QMessageBox.question(self, "Confirm", "Delete this project?")
        if reply == QMessageBox.Yes:
            try:
                os.remove(path)
                self.table.removeRow(row)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Delete failed:\n{e}")