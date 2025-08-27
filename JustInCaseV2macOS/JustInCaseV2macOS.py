import os
import sys

import whisper
from datetime import timedelta

import platform # for platform identification

from PySide6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QTextEdit, QLabel, QHBoxLayout)
from PySide6.QtGui import QFont, Qt, QPixmap, QIcon
from PySide6.QtCore import QThread, Signal  # QThread is required so GUI doesn't freeze, Signal makes the thread communicate back to main GUI thread safely


class JustInCaseCore:
    def __init__(self):
        self.model = whisper.load_model("small")

    def format_timestampt(self, seconds):
        td = timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        milliseconds = int((td.total_seconds() - total_seconds) * 1000)
        return str(td).split(".")[0].zfill(8) + f",{milliseconds:03d}"

    def listern_and_generate_srt(self, audio_path):
        result = self.model.transcribe(audio_path)

        base, _ = os.path.splitext(audio_path)
        srt_output_path = f"{base}_subtitles.srt"

        with open(srt_output_path, "w", encoding="utf-8") as srt_file:
            for i, segment in enumerate(result["segments"], start=1):
                start = self.format_timestampt(segment["start"])
                end = self.format_timestampt(segment["end"])
                text = segment["text"].strip()

                srt_file.write(f"{i}\n")
                srt_file.write(f"{start} --> {end}\n")
                srt_file.write(f"{text}\n\n")


        # print(f"SRT file saved: {srt_output_path}")
        # print(Fore.LIGHTYELLOW_EX + "Note: Review the subtitles. Some words may be inaccurate or misheard ")
        return srt_output_path

# Ugh this class... this class is to prevent GUI from not going black (I mean "not responding" thing)
class TranscriptionThread(QThread):  # this custom class inherits from QThread
    finished = Signal(str)  # custom signal that the thread will emit when transcription finishes succesfully
    error = Signal(str)  # an error signal

    def __init__ (self, core, audio_path):
        super().__init__()
        self.core = core
        self.audio_path = audio_path

    def run(self):  # run is the special method of a QThread that executes in new thread, not in the main GUI Thread
        try:
            srt_path = self.core.listern_and_generate_srt(self.audio_path)
            self.finished.emit(srt_path)

        except Exception as e:
            self.error.emit(str(e))


class JustInCaseGUI(QWidget):
    def __init__(self):
        super().__init__() # this is used to call the constructor of the parent class of the current class, Here it inherited from QWidget
        # QWidget is basically like blank canvas. u can add buttons, labels, set layouts, etc.

        self.setWindowTitle("JustInCase V2 – Subtitle Generator By Mr. BILRED")
        self.setGeometry(100, 100, 800, 700)  # (x, y, width, height)
        self.setFixedSize(800, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;  /* Almost black */
                color: #f5f5f7;  /* like macOS dark mode text */
            }
            QPushButton {
                background-color: #3a3a3c;  /* dark gray with a touch of blue */
                color: white;
                border: 1px solid #48484a; 
                padding: 6px;
                border-radius: 5px
            }
            QPushButton:hover {
                background-color: #48484a;   /* medium-dark gray, a lil lighter than #3a3a3c */
            }
            QTextEdit {
                background-color: #2c2c2c;  /* deep charcoal gray */
                color: #d1d1d1;  /* light gray text */
            }
        """)
        self.setWindowIcon(QIcon("JUSTINCASELOGO.icns"))
        self.setAcceptDrops(True) # Drag and drop feature

        # Left Bottom
        os_name = platform.system()
        if os_name == "Darwin":
            mac_version, _, _ = platform.mac_ver()  # this returns a tuple of 3 values, it just get 1st one with this logic
            if mac_version:
                os_name = f"macOS {mac_version}"
            else:
                os_name = "Darwin"

        self.os_label = QLabel(f"{os_name}", self)  # the second "self" makes the label a child widget of the main windows
        self.os_label.setStyleSheet("color: gray; font-size: 10px;")
        self.os_label.adjustSize()
        # print(self.os_label.height())
        self.os_label.move(20, self.height() - self.os_label.height() - 5 )
        self.os_label.show()

        # Right Bottom thing
        operating_system_label = QLabel("JustInCase for macOS", self)
        operating_system_label.setStyleSheet("color: gray; font-size: 10px;")
        operating_system_label.adjustSize()
        operating_system_label.move(self.width()  - operating_system_label.width() - 20, self.height() - 17)
        # in the above thing, self.width() is the main window's current width
        # operating_system_label.width() is the width of the label text
        # - 10 means a little padding from the right edge
        # For the height, self.height() is the height of main window's current height and -10 makes it a lil upward
        operating_system_label.show()



        self.audio_path = None
        self.core = JustInCaseCore()  # this allows GUI to use functions from JustInCaseCore (cli backend)

        layout = QVBoxLayout()  # this creates vertical layout.
        button_layout = QHBoxLayout()  # this creates horizontal layout
        # No need to modify this layout later, so no need to use self.


        title_label = QLabel("JustInCase V2")
        title_font = QFont("Arial", 24, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white;")
        layout.addWidget(title_label)


        subtitle_label = QLabel("Subtitle Generator By Mr. BILRED \nJust In Case You Need Them")
        subtitle_font = QFont("Arial", 16)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: white;")
        layout.addWidget(subtitle_label)


        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/asset1.png")
        logo_label.setPixmap(logo_pixmap.scaledToHeight(40, Qt.SmoothTransformation))


        header_layout = QHBoxLayout()
        header_layout.addWidget(title_label, alignment=Qt.AlignLeft)
        header_layout.addWidget(subtitle_label, alignment=Qt.AlignLeft)



        header_layout.addStretch()
        header_layout.addWidget(logo_label, alignment=Qt.AlignRight)
        layout.addLayout(header_layout)


        # Buttons
        self.browse_button = QPushButton("Browse Audio/Video File")
        self.generate_button = QPushButton("Generate SRT")
        self.generate_button.setEnabled(False)  # this means unless a file is selected, generate_button is unclickable

        # When Buttons are Clicked

        self.browse_button.clicked.connect(self.browse_audio_file)  # this function should be defined below
        self.generate_button.clicked.connect(self.generate_srt)
        # self.generate_button.clicked.connect(self.generate_srt)

        self.draganddropLabel = QLabel("Drag & Drop", self)
        self.draganddropLabel.setAlignment(Qt.AlignCenter)
        self.draganddropLabel.setStyleSheet("""
              QLabel {
              border: 2px dashed gray;
              color: gray;
              font-size: 14px;
              padding: 40px;
              }
              """)
        layout.addWidget(self.draganddropLabel)

        self.log_output = QTextEdit()  # this creates a text area in gui where logs, messages, errors, etc can be shown
        self.log_output.setReadOnly(True) # this makes QTextEdit read only

        button_layout.addWidget(self.browse_button)  # just see, i used button_layout, which is horizontal!
        button_layout.addWidget(self.generate_button)

        layout.addLayout(button_layout)
        layout.addWidget(QLabel("Log Output:")) # this creates a label right above the text area
        layout.addWidget(self.log_output) # this adds the actual text area for logs under the label

        self.setLayout(layout)

    def log(self, message):
        self.log_output.append(message)

    def dragEnterEvent(self, event):  # initially I set it to dragEvent function name, but somehow I got to know Qt only calls dragEnterEvent
        if event.mimeData().hasUrls():  # this checks if its a file
            event.acceptProposedAction()  # accept the dragged thing
            self.draganddropLabel.setStyleSheet("""
            QLabel {
            border: 2px dashed gray;
            color: gray;
            font-size: 14px;
            padding: 40px;
            background-color: #2a2a2a;  /* soft blue highlight */
            
            }
            """)
            self.draganddropLabel.setText("Drop The File")
        else:
            event.ignore()

    # def dragMoveEvent(self, event):
    #     self.draganddropLabel.setStyleSheet("""
    #     QLabel {
    #         border: 2px dashed gray;
    #         color: gray;
    #         font-size: 14px;
    #         padding: 40px;
    #         background-color: #e0ffe0;
    #     }
    #     """)

    def dragLeaveEvent(self, event):
        self.draganddropLabel.setStyleSheet("""
        QLabel {
            border: 2px dashed gray;
            color: gray;
            font-size: 14px;
            padding: 40px;
            background-color: transparent;
        }  
        """)
        self.draganddropLabel.setText("Drag & Drop")

    def dropEvent(self, event):
        urls = event.mimeData().urls()  # this gives the data being dropped. .urls() tries to get it as a list of file URLs
        if urls:
            file_path = urls[0].toLocalFile() # this gets the first file path
            self.audio_path = file_path
            self.generate_button.setEnabled(True) # makes the "Generate SRT" button Clickable
            self.log(f"File Selected via Drag & Drop: {file_path}")
            self.log("Wait for a while after you press Generate SRT button")
            # self.draganddropLabel.hide()

    def browse_audio_file(self):
            file_path, _ = QFileDialog.getOpenFileName(self, "Select Audio/Video File", "", "All Files (*)")
            if file_path:
                self.audio_path = file_path
                self.generate_button.setEnabled(True)
                self.log(f"File Selected: {file_path}")
                self.log("\nWhen You Press Generate SRT button, Wait For A While...")

    def when_transcription_done(self, srt_path): # A callback way. Its called when the transcription thread finishes successfully
        self.log(f"\nSRT File Saved: {srt_path}")
        self.log("NOTE: Review the subtitles. Some words 'can' be inaccurate or misheard")
        self.generate_button.setEnabled(True) # when it's done, the button should get alive

    def when_transcription_error_uncle(self, error_uncle):
        self.log(f"\nERROR: {error_uncle}")
        self.generate_button.setEnabled(True)

    def generate_srt(self):
        if not self.audio_path:
            self.log("NO FILE SELECTED")
            return

        self.generate_button.setEnabled(False)
        self.log("Transcription Started... Sit tight")

        self.thread = TranscriptionThread(self.core, self.audio_path) # creates a new thread for transcription. self.thread() is an object of that TranscriptionThread class
        self.thread.finished.connect(self.when_transcription_done)
        self.thread.error.connect(self.when_transcription_error_uncle)
        self.thread.finished.connect(self.thread.deleteLater) # when transcription is done, Qt will automatically delete the thread object at a safe time.
        self.thread.error.connect(self.thread.deleteLater) # if an error occurs, thread gets deleted
        self.thread.start()  # Tells Qt to start a new thread. Qt will call the thread's .run() method in the new thread.

        # try:
        #     # self.log("\nAttempting to generate SRT...")
        #     srt_output_path = self.core.listern_and_generate_srt(self.audio_path)
        #     self.log(f"\nSRT File Saved: {srt_output_path}")
        #     self.log("NOTE: Review the subtitles. Some words may be inaccurate or misheard")
        #
        # except Exception as e:
        #     self.log(f"ERROR: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JustInCaseGUI()
    window.show()
    sys.exit(app.exec())  # this ensures when the app closes, Python exits cleanly.



# Mr. BILRED

