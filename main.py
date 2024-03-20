# program umożliwiający analizę spektralną plików dźwiękowych
import PyQt5.QtGui
from PyQt5 import uic, QtWidgets
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import sys
import wave
rng = np.random.default_rng()
from scipy.io import wavfile
import os
form, _ = uic.loadUiType("widok.ui")

class MainWindow(QtWidgets.QMainWindow, form):
    wybrany_plik = ""
    data = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.Button_open.clicked.connect(self.wybierz_plik)
        self.Button_generate.clicked.connect(self.wygeneruj_spektrogram)
        self.Button_save.clicked.connect(self.zapisz_spektrogram)
        self.comboBox_okna.currentIndexChanged.connect(self.wygeneruj_spektrogram)
        self.figure = Figure()
        self.figureCanvas = FigureCanvasQTAgg(self.figure)
        self.show()

    def wybierz_plik(self):
        pom = QtWidgets.QFileDialog.getOpenFileName(None,
                                                    "otwórz plik .wav",
                                                    "/Images",
                                                    "Images (*.wav)")
        if not pom[0]:
            return
        self.wybrany_plik = pom[0]
        self.wygeneruj_spektrogram()

    def wybierz_stopien_nachodzenia(self):
        self.spinBox_st_nachodzenia.currentIndexChanged.connect(self.wybierz_stopien_nachodzenia)

    def ustaw_overlap(self):
        self.overlap = int(self.nfft * self.spinBox_st_nachodzenia.value() / 100)

    def ustaw_nfft(self):
            t = self.comboBox_nfft.currentText()
            if t == "Wąskopasmowy":
                self.nfft = int(len(self.data) / self.sample_rate * 300)
            else:
                self.nfft = int(len(self.data) / self.sample_rate * 25)

    def ustaw_funkcje_okna(self):
        funkcja_okna = self.comboBox_okna.currentText()
        if funkcja_okna == "Kaisera":
            return np.kaiser(self.nfft, 1)
        if funkcja_okna == "Hamminga":
            return np.hamming(self.nfft)
        if funkcja_okna == "Barletta":
            return np.bartlett(self.nfft)

    def wygeneruj_spektrogram(self):
        plt.clf()
        fs = 10e3
        N = 1e5
        amp = 2 * np.sqrt(2)
        try:
            self.sample_rate, self.data = wavfile.read(self.wybrany_plik)
        except:
            print("plik nie zostal wczytany")
        try:
            self.ustaw_nfft()
            window_f = self.ustaw_funkcje_okna()
            self.ustaw_overlap()
        except Exception as E:                                  #Myśle że jeśli te wartości nie są zainicjalizowane to można po porstu pominąć
            if not self.data or not self.sample_rate:           #ten kawałek kodu. Wartosci w komórkach pozostają zmienione, a przy generowaniu spektogramu
                pass                                            #kod i tak dostosowuje wartości do tego co akualnie jest w komórkach
            else:
                print(E)
        try:
            self.plt = plt.specgram(self.data, Fs=self.sample_rate, NFFT=self.nfft, cmap=plt.get_cmap('autumn_r'),
                                    window=window_f, noverlap=self.overlap)
        except Exception as E:
            if not self.data or not self.sample_rate:
                pass
            else:
                print(E)
            return
        try:
            plt.savefig("temp.png")
            pixmap = PyQt5.QtGui.QPixmap("temp.png")
            self.label_spektogram.setPixmap(pixmap)
            self.label_spektogram.show()
            os.remove("temp.png")
        except Exception as F:
            print(F)

    def zapisz_spektrogram(self):
        spektrogram, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Zapisz",
            ".png",
            "Wszystkie pliki (*);;" +
            "Pliki bitmapowe (*.png *.jpg);;" +
            "Pliki wektorowe (*.svg *.pdf)",
        )
        plt.savefig(spektrogram)

    def odtworz_dzwiek(self):
        wf = wave.open(self.wybrany_plik)
        plik_we = pyaudio.PyAudio()
        stream = plik_we.open(
            format=plik_we.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True
        )
        data = wf.readframes(1024)

        while len(data):
            stream.write(data)
            data = wf.readframes(1024)

        stream.stop_stream()
        stream.close()
        plik_we.terminate()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec())

