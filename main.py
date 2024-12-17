import sys
import time
import random

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QTextEdit, QPushButton, 
    QListWidget, QDialog, QHBoxLayout, QLabel, QDialogButtonBox, QListWidgetItem, QMessageBox)

class PlaylistCreator(QWidget):
    def __init__(self):
        super().__init__()

        self.start_time = None
        self.completion_times = []

        self.setWindowTitle("Playlist Creator")
        self.setGeometry(100, 100, 400, 500)

        self.layout = QVBoxLayout()
        
        self.playlist_name = QLineEdit(self)
        self.playlist_name.setPlaceholderText("Название плейлиста")
        self.playlist_name.textChanged.connect(self.check_task_completion)
        self.layout.addWidget(self.playlist_name)

        self.playlist_description = QLineEdit(self)
        self.playlist_description.setPlaceholderText("Описание плейлиста")
        self.playlist_description.textChanged.connect(self.check_task_completion)
        self.layout.addWidget(self.playlist_description)

        self.music_list = QListWidget(self)
        self.layout.addWidget(self.music_list)

        self.add_music_button_top = QPushButton("+ Добавить аудиозапись", self)
        self.add_music_button_top.clicked.connect(self.open_music_selection_dialog)
        self.layout.addWidget(self.add_music_button_top)

        self.setLayout(self.layout)

        with open('dict.txt', 'r') as file:
            self.words = file.readlines()
            self.words = [s.strip("\n") for s in self.words]

        self.all_songs = ["Fifteen Feet of Pure White Snow", "Bound 2", "All I Want for Christmas Is You", "Somethin' Stupid", "New Years End", \
            "If Darkness Had a Son", "Fill Your Brains", "The Great Sleep", "Needles and Pins", "Hollywood Whore", "Don't Call My Name", "Black Milk", \
                "Mary Jane's Last Dance", "True Love Waits", "Poison's Gone", "Back Against The Wall", "This Isn't the Place", "The Chemicals Between Us" \
                    , "Charlie", "The Negative One", "I Can't Go on Without You", "Kill For You", "My Own Summer (Shove It)", "Rein raus", "What, Me Worry?"]
        self.generate_new_task()

    def generate_new_task(self):
        self.target_name = self.random_word()
        self.target_description = " ".join(self.random_word() for _ in range(random.randint(2, 5)))
        self.target_songs = random.sample(self.all_songs, k=random.randint(4, 7))

        self.start_time = time.time()
        self.show_task_window()
        self.music_list.clear()
        self.playlist_name.clear()
        self.playlist_description.clear()

    def random_word(self):
        return random.choice (self.words)

    def show_task_window(self):
        self.task_window = QDialog(self)
        self.task_window.setWindowTitle("Task Description")
        self.task_window.setGeometry(150, 150, 300, 200)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Название: {self.target_name}"))
        layout.addWidget(QLabel(f"Описание: {self.target_description}"))
        layout.addWidget(QLabel(f"Аудиозаписи: {', '.join(self.target_songs)}"))

        self.task_window.setLayout(layout)
        self.task_window.show()

    def open_music_selection_dialog(self):
        dialog = MusicSelectionDialog(self)
        dialog.exec_()

        selected_song = dialog.selected_song
        if selected_song:
            if not self.is_song_in_playlist(selected_song):
                self.add_song_to_playlist(selected_song)
            else:
                QMessageBox.warning(self, "Duplicate Song", f"'{selected_song}' is already in the playlist.")

        self.check_task_completion()

    def is_song_in_playlist(self, song):
        return song in self.get_playlist_songs()

    def add_song_to_playlist(self, song):
        item = QListWidgetItem()

        remove_button = QPushButton("Убрать", self)
        remove_button.clicked.connect(lambda: self.remove_song_from_playlist(item))

        layout = QHBoxLayout()
        layout.addWidget(QLabel(song))
        layout.addWidget(remove_button)

        widget = QWidget()
        widget.setLayout(layout)

        item.setSizeHint(widget.sizeHint())
        self.music_list.addItem(item)
        self.music_list.setItemWidget(item, widget)
        self.check_task_completion()

    def remove_song_from_playlist(self, item):
        self.music_list.takeItem(self.music_list.row(item))
        self.check_task_completion()

    def check_task_completion(self):
        name_correct = self.playlist_name.text() == self.target_name
        description_correct = self.playlist_description.text() == self.target_description
        songs_correct = set(self.target_songs).issubset(set(self.get_playlist_songs()))

        if name_correct and description_correct and songs_correct:
            self.record_completion_time()

    def get_playlist_songs(self):
        songs = []
        for i in range(self.music_list.count()):
            item = self.music_list.item(i)
            widget = self.music_list.itemWidget(item)
            if widget:
                label = widget.findChild(QLabel)
                if label:
                    songs.append(label.text())
        return songs

    def record_completion_time(self):
        end_time = time.time()
        duration = end_time - self.start_time
        self.completion_times.append(duration)
        self.show_completion_window()

    def show_completion_window(self):
        completion_dialog = QDialog(self)
        completion_dialog.setWindowTitle("Task Completed")
        completion_dialog.setGeometry(150, 150, 400, 200)

        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"Задание выполнено за {self.completion_times[-1]:.2f} секунд"))

        layout.addWidget(QLabel("Общая статистика:"))
        times_label = QLabel("\n".join(f"Задание {i + 1}: {time:.2f} секунд" for i, time in enumerate(self.completion_times)))
        layout.addWidget(times_label)
        
        layout.addWidget(QLabel(f"Среднее время: {sum(self.completion_times) / len(self.completion_times):.2f} секунд."))

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(lambda: [completion_dialog.accept(), self.generate_new_task()])
        layout.addWidget(buttons)

        completion_dialog.setLayout(layout)
        completion_dialog.exec_()

class MusicSelectionDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Select Music")
        self.setGeometry(150, 150, 300, 400)

        self.selected_song = None
        self.layout = QVBoxLayout()

        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Поиск")
        self.search_bar.textChanged.connect(self.filter_songs)
        self.layout.addWidget(self.search_bar)

        self.song_list = QListWidget(self)
        self.parent_songs = parent.get_playlist_songs()
        self.populate_song_list(parent.all_songs)
        self.layout.addWidget(self.song_list)

        self.setLayout(self.layout)

    def populate_song_list(self, songs):
        self.song_list.clear()
        for song in songs:
            if song not in self.parent_songs:
                item = QListWidgetItem(song)
                self.song_list.addItem(item)

        self.song_list.itemClicked.connect(self.select_song)

    def filter_songs(self, query):
        filtered_songs = [song for song in self.parent().all_songs if query.lower() in song.lower()]
        self.populate_song_list(filtered_songs)

    def select_song(self, item):
        self.selected_song = item.text()
        self.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlaylistCreator()
    window.show()
    sys.exit(app.exec_())
