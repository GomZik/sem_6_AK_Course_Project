#-*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys, math, time, shelve, os
from nn_new import generate
from Ui_MWindow import Ui_MWindow

class Logger():
    def __init__(self, txt_logger):
        self.txt_logger = txt_logger
        
    def write(self, string):
        self.txt_logger.appendPlainText(string.strip())
        
    def writelines(self, lines):
        for line in lines:
            self.write(line)

class ProcessThread(QThread):
    
    progress_changed = pyqtSignal(int)
    progress_complete = pyqtSignal(QImage)
    
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        
    def run(self):
        if os.path.exists('weights.dat'):
            os.remove('weights.dat')
        new_image = QImage(self.image.width(), self.image.height(), QImage.Format_RGB32)
        for i in xrange(self.nn_count):
            width = int(math.ceil(float(self.image.width()) / self.h_parts))
            x = (i % self.h_parts) * width
            height = int(math.ceil(float(self.image.height()) / self.v_parts))
            y = (i / self.h_parts) * height
            #print x, y, width, height
            #print 'creating network number %d' % i
            nn = generate(
                (int(self.inputs), int(self.hidden), int(self.inputs))
            )
            image_part = self.image.copy(x, y, width, height)
            inputs = []
            for pix_y in xrange(height):
                for pix_x in xrange(width):
                    pix_rgb = QColor(image_part.pixel(pix_x, pix_y))
                    #print pix_rgb.redF(), pix_rgb.greenF(), pix_rgb.blueF()
                    #print 'x = %d, y = %d' % (x+pix_x, y+pix_y)
                    inputs.append(pix_rgb.redF())
                    inputs.append(pix_rgb.greenF())
                    inputs.append(pix_rgb.blueF())
            #print 'learning network'
            nn.learn(
                [
                    [inputs, inputs]
                ], self.max_error
            )
            #print nn.get_all_weights()
            w = shelve.open('weights.dat')
            w[str(i)] = nn.get_decompress_weights()
            w[str(i) + 'data'] = nn.get_compressed_data()
            w.close()
            #print 'taking output'
            #print inputs
            outputs = nn.calculate(inputs)
            #print outputs
            for j in xrange(0, len(outputs), 3):
                pix_x = x + (j / 3) % width
                pix_y = y + (j / 3) / width
                if pix_x >= self.image.width(): continue
                if pix_y >= self.image.height(): continue
                #print 'new: j = %d, width = %d x = %d, y = %d' % (j, width, pix_x, pix_y)
                pix_red = outputs[j]
                if pix_red > 1: pix_red = 1
                if pix_red < 0: pix_red = 0
                pix_green = outputs[j+1]
                if pix_green > 1: pix_green = 1
                if pix_green < 0: pix_green = 0
                pix_blue = outputs[j+2]
                if pix_blue > 1: pix_blue = 1
                if pix_blue < 0: pix_blue = 0
                new_image.setPixel(pix_x, pix_y, QColor.fromRgbF(pix_red, pix_green, pix_blue).rgb())
            progress = int(math.floor(float(i * 100) / self.nn_count))
            self.progress_changed.emit(progress)
        self.progress_complete.emit(new_image)

class MWindow(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.ui = Ui_MWindow()
        self.ui.setupUi(self)
        
        #sys.stdout = Logger(self.ui.txt_logger)
        
        self.ui.btn_load_image.clicked.connect(self.load_image_clicked)
        self.ui.btn_next1.clicked.connect(self.next_clicked)
        self.ui.btn_back2.clicked.connect(self.back_clicked)
        self.ui.btn_next2.clicked.connect(self.process)
        
    def load_image_clicked(self):
        image_path = QFileDialog.getOpenFileName(self, u'Изображение', '.', u'Изображения (*.jpg *.png)')
        if not image_path.isNull():
            image_path = unicode(image_path)
            self.image = QImage(image_path)
            self.ui.txt_h_parts.setValue(int(math.ceil(float(self.image.width()) / 3)))
            self.ui.txt_v_parts.setValue(int(math.ceil(float(self.image.height()) / 3)))
            pixmap = QPixmap.fromImage(self.image)
            sc = QGraphicsScene()
            sc.addPixmap(pixmap)
            self.ui.image_preview.setScene(sc)
            self.ui.image_preview.repaint()
            self.ui.btn_next1.setEnabled(True)
    
    def next_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(self.ui.stackedWidget.currentIndex() + 1)
    
    def back_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(self.ui.stackedWidget.currentIndex() - 1)
        
    def process(self):
        self.ui.page_2.setEnabled(False)
        self.thread = ProcessThread(self)
        self.thread.nn_count = int(self.ui.txt_h_parts.value() * self.ui.txt_v_parts.value())
        print u'Нейронных сетей: %d' % int(self.thread.nn_count)
        self.thread.inputs = int(math.ceil(float(self.image.width()) / self.ui.txt_h_parts.value()) * math.ceil(float(self.image.height()) / self.ui.txt_v_parts.value()) * 3)
        print u'Входов для каждой: %d' % int(self.thread.inputs)
        self.thread.hidden = int(self.ui.txt_zip.value())
        #self.thread.hidden = 120
        print u'Нейронов на скрытом слое: %d' % int(self.thread.hidden)
        self.thread.h_parts = self.ui.txt_h_parts.value()
        self.thread.v_parts = self.ui.txt_v_parts.value()
        self.thread.image = self.image
        self.thread.max_error = self.ui.txt_max_error.value()
        self.thread.progress_changed.connect(self.progress_changed)
        self.thread.progress_complete.connect(self.progress_complete)
        self.thread.start()
        
    def progress_changed(self, progress):
        self.ui.progressBar.setValue(progress)
        
    def progress_complete(self, new_image):
        pixmap = QPixmap.fromImage(self.image)
        sc = QGraphicsScene()
        sc.addPixmap(pixmap)
        self.ui.before.setScene(sc)
        self.ui.before.repaint()
        pixmap = QPixmap.fromImage(new_image)
        sc = QGraphicsScene()
        sc.addPixmap(pixmap)
        self.ui.after.setScene(sc)
        self.ui.after.repaint()
        self.next_clicked()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MWindow()
    window.show()
    app.exec_()