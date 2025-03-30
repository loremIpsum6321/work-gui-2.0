import sys
import os
import csv
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QFileDialog,
    QMessageBox,
    QProgressBar,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class CSVConverterThread(QThread):
    """
    Thread for converting CSV files in a directory.
    """

    conversion_finished = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    error_occurred = pyqtSignal(str)

    def __init__(self, input_dir, output_dir):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.is_running = True

    def run(self):
        """
        Converts all CSV files in the input directory.
        """
        try:
            csv_files = [
                f
                for f in os.listdir(self.input_dir)
                if os.path.isfile(os.path.join(self.input_dir, f))
                and f.lower().endswith(".csv")
            ]
            total_files = len(csv_files)
            converted_count = 0

            for file_name in csv_files:
                if not self.is_running:
                    break
                input_file_path = os.path.join(self.input_dir, file_name)
                output_file_path = os.path.join(
                    self.output_dir, os.path.splitext(file_name)[0] + "_converted.txt"
                )

                try:
                    self.convert_csv(input_file_path, output_file_path)
                    converted_count += 1
                    progress = int((converted_count / total_files) * 100)
                    self.progress_updated.emit(progress)
                except Exception as e:
                    self.error_occurred.emit(f"Error converting {file_name}: {e}")
                    return

            self.conversion_finished.emit("CSV conversion completed successfully!")

        except Exception as e:
            self.error_occurred.emit(f"An error occurred: {e}")

    def convert_csv(self, input_file, output_file):
        """
        Converts a single CSV file to a text file.
        """
        with open(input_file, "r", newline="", encoding="utf-8") as csvfile, open(
            output_file, "w", encoding="utf-8"
        ) as outfile:
            reader = csv.reader(csvfile)
            for row in reader:
                outfile.write("\t".join(row) + "\n")

    def stop(self):
        self.is_running = False
        self.wait()


class CSVConverterApp(QWidget):
    """
    Main application window for CSV conversion.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Converter")
        self.setGeometry(100, 100, 500, 200)

        self.input_file_path = None
        self.input_dir_path = None
        self.output_dir_path = None
        self.converter_thread = None

        self.init_ui()

    def init_ui(self):
        """
        Initializes the user interface.
        """
        layout = QVBoxLayout()

        # Input CSV File
        input_file_layout = QHBoxLayout()
        self.input_file_label = QLabel("Input CSV File:")
        self.input_file_line_edit = QLineEdit()
        self.input_file_line_edit.setReadOnly(True)
        self.browse_file_button = QPushButton("Browse")
        self.browse_file_button.clicked.connect(self.browse_input_file)
        input_file_layout.addWidget(self.input_file_label)
        input_file_layout.addWidget(self.input_file_line_edit)
        input_file_layout.addWidget(self.browse_file_button)
        layout.addLayout(input_file_layout)

        # Input Directory
        input_dir_layout = QHBoxLayout()
        self.input_dir_label = QLabel("Input Directory:")
        self.input_dir_line_edit = QLineEdit()
        self.input_dir_line_edit.setReadOnly(True)
        self.browse_input_dir_button = QPushButton("Browse")
        self.browse_input_dir_button.clicked.connect(self.browse_input_directory)
        input_dir_layout.addWidget(self.input_dir_label)
        input_dir_layout.addWidget(self.input_dir_line_edit)
        input_dir_layout.addWidget(self.browse_input_dir_button)
        layout.addLayout(input_dir_layout)

        # Output Directory
        output_dir_layout = QHBoxLayout()
        self.output_dir_label = QLabel("Output Directory:")
        self.output_dir_line_edit = QLineEdit()
        self.output_dir_line_edit.setReadOnly(True)
        self.browse_output_dir_button = QPushButton("Browse")
        self.browse_output_dir_button.clicked.connect(self.browse_output_directory)
        output_dir_layout.addWidget(self.output_dir_label)
        output_dir_layout.addWidget(self.output_dir_line_edit)
        output_dir_layout.addWidget(self.browse_output_dir_button)
        layout.addLayout(output_dir_layout)

        # Convert Button
        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self.start_conversion)
        layout.addWidget(self.convert_button)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Cancel Button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_conversion)
        self.cancel_button.setEnabled(False)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def browse_input_file(self):
        """
        Opens a file dialog to select the input CSV file.
        """
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv)"
        )
        if file_name:
            self.input_file_path = file_name
            self.input_file_line_edit.setText(file_name)

    def browse_input_directory(self):
        """
        Opens a directory dialog to select the input directory.
        """
        dir_name = QFileDialog.getExistingDirectory(
            self, "Select Input Directory", ""
        )
        if dir_name:
            self.input_dir_path = dir_name
            self.input_dir_line_edit.setText(dir_name)

    def browse_output_directory(self):
        """
        Opens a directory dialog to select the output directory.
        """
        dir_name = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", ""
        )
        if dir_name:
            self.output_dir_path = dir_name
            self.output_dir_line_edit.setText(dir_name)

    def start_conversion(self):
        """
        Starts the CSV conversion process.
        """
        if not self.input_dir_path:
            QMessageBox.warning(self, "Warning", "Please select an input directory.")
            return
        if not self.output_dir_path:
            QMessageBox.warning(self, "Warning", "Please select an output directory.")
            return

        self.convert_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setValue(0)

        self.converter_thread = CSVConverterThread(
            self.input_dir_path, self.output_dir_path
        )
        self.converter_thread.conversion_finished.connect(self.on_conversion_finished)
        self.converter_thread.progress_updated.connect(self.on_progress_updated)
        self.converter_thread.error_occurred.connect(self.on_error_occurred)
        self.converter_thread.start()

    def on_conversion_finished(self, message):
        """
        Handles the completion of the CSV conversion.
        """
        QMessageBox.information(self, "Success", message)
        self.convert_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(100)

    def on_progress_updated(self, progress):
        """
        Updates the progress bar.
        """
        self.progress_bar.setValue(progress)

    def on_error_occurred(self, error_message):
        """
        Handles errors during the conversion process.
        """
        QMessageBox.critical(self, "Error", error_message)
        self.convert_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    def cancel_conversion(self):
        """
        Cancels the CSV conversion process.
        """
        if self.converter_thread:
            self.converter_thread.stop()
            self.convert_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
            self.progress_bar.setValue(0)
            QMessageBox.information(self, "Cancelled", "Conversion cancelled.")


def main():
    """
    Main function to start the application.
    """
    app = QApplication(sys.argv)
    window = CSVConverterApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
