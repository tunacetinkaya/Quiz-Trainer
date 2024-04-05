import sys
import json
import random
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self, questions, exam_mode=False, start=0, end=0):
        super(MainWindow, self).__init__()
        self.browser = QWebEngineView()
        self.questions = questions
        self.exam_mode = exam_mode
        self.start = start
        self.end = end
        self.current_number = str(next(iter(self.questions)))
        self.browser.setUrl(QUrl(self.questions.get(self.current_number)))
        self.setCentralWidget(self.browser)
        self.showMaximized()

        self.seed = 0
        random.seed(self.seed)

        navbar = QToolBar()
        self.addToolBar(navbar)

        previous_btn = QAction("Previous", self)
        previous_btn.triggered.connect(self.previous_question)
        navbar.addAction(previous_btn)

        next_btn = QAction("Next", self)
        next_btn.triggered.connect(self.next_question)
        navbar.addAction(next_btn)

        find_btn = QAction("Find", self)
        find_btn.triggered.connect(self.find_question)
        navbar.addAction(find_btn)

        self.url_bar = QLineEdit()
        self.url_bar.setText(self.current_number)
        self.url_bar.returnPressed.connect(self.find_question)
        navbar.addWidget(self.url_bar)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.previous_question()
        elif event.key() == Qt.Key_Right:
            self.next_question()

    def find_question(self):
        question_num = self.url_bar.text()
        if not question_num == self.current_number:
            question_url = self.questions.get(question_num)
            if question_url:
                self.browser.setUrl(QUrl(question_url))
                self.url_bar.setText(question_num)
                self.current_number = question_num
            else:
                QMessageBox.warning(
                    self,
                    "Question",
                    "Question Not Found. Please only enter an existing question number.",
                )
                self.url_bar.setText(self.current_number)

    def previous_question(self):
        if self.exam_mode:
            if self.seed > 0:
                self.seed -= 1
                random.seed(self.seed)
                question_num = str(random.randint(self.start, self.end))
                question_url = self.questions.get(question_num)
                if question_url:
                    self.browser.setUrl(QUrl(question_url))
                    self.url_bar.setText(question_num)
                    self.current_number = question_num

            else:
                QMessageBox.warning(
                    self, "Question", "There is no previous question in exam mode."
                )
                self.url_bar.setText(self.current_number)
        else:
            if not self.current_number == "1":
                question_num = str((int(self.current_number) - 1))
                question_url = self.questions.get(question_num)
                if question_url:
                    self.browser.setUrl(QUrl(question_url))
                    self.url_bar.setText(question_num)
                    self.current_number = question_num
            else:
                QMessageBox.warning(self, "Question", "There is no previous question.")
                self.url_bar.setText(self.current_number)

    def next_question(self):
        if self.exam_mode:
            self.seed += 1
            random.seed(self.seed)
            question_num = str(random.randint(self.start, self.end))
            question_url = self.questions.get(question_num)
            if question_url:
                self.browser.setUrl(QUrl(question_url))
                self.url_bar.setText(question_num)
                self.current_number = question_num
            else:
                QMessageBox.warning(
                    self,
                    "Question",
                    f"There is no question number {question_num} please change the end parameter to {len(self.questions)} in the run command.",
                )
                self.url_bar.setText(self.current_number)
        else:
            question_num = str((int(self.current_number) + 1))
            question_url = self.questions.get(question_num)
            if question_url:
                self.browser.setUrl(QUrl(question_url))
                self.url_bar.setText(question_num)
                self.current_number = question_num
            else:
                QMessageBox.warning(self, "Question", "There is no next question.")
                self.url_bar.setText(self.current_number)


def main():
    exam_mode = False
    exam_range = None
    json_file_path = None
    start = 0
    end = 0

    if len(sys.argv) == 4 and sys.argv[2] == "--exam":
        exam_mode = True
        exam_range = sys.argv[3].split("-")
        if len(exam_range) != 2:
            print("Invalid exam range. Please specify in the format 'start-end'.")
            sys.exit(1)
        try:
            start = int(exam_range[0])
            end = int(exam_range[1])
        except ValueError:
            print("Invalid exam range. Please specify in integers.")
            sys.exit(1)
        if start >= end:
            print("Invalid exam range. Start number should be less than end number.")
            sys.exit(1)
        json_file_path = sys.argv[1]

    elif len(sys.argv) == 3 and sys.argv[1] == "--exam":
        print(
            "Please provide the JSON file path along with the --exam flag and exam range."
        )
        sys.exit(1)
    elif len(sys.argv) == 2:
        json_file_path = sys.argv[1]
    else:
        print("Usage: python main.py <json_file_path> [--exam start-end]")
        sys.exit(1)

    if not json_file_path:
        print("Usage: python main.py <json_file_path> [--exam start-end]")
        sys.exit(1)

    questions = read_json_file(json_file_path)
    print(len(questions), "questions loaded.")

    app = QApplication(sys.argv)
    QApplication.setApplicationName("Quiz Trainer")

    app_icon = QIcon("resources/icons/app_icon.png")
    app.setWindowIcon(app_icon)

    window = MainWindow(questions, exam_mode, start, end)
    app.exec_()


def read_json_file(file_path):
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    return data


if __name__ == "__main__":
    main()
