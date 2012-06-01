#-*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys, math, time, shelve, os
from nn_new import generate
from Ui_MWindow import Ui_MWindow

class ProcessThread(QThread):
    
    progress_changed = pyqtSignal(int)
    progress_complete = pyqtSignal(QImage)
    
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        
    def run(self):
        if os.path.exists('weights.dat'):
            os.remove('weights.dat')
        new_image = QImage(self.image.width(), self.image.height(), QImage.Format_RGB32)
        nn = generate(
            (int(self.inputs), int(self.hidden), int(self.inputs))
        )
        iteration = True
        i_count = 0
        c = []
        width = int(math.ceil(float(self.image.width()) / self.h_parts))
        height = int(math.ceil(float(self.image.height()) / self.v_parts))
        while iteration:
            if i_count == 0: iteration = False
            error = 0.0
            for i in xrange(self.nn_count):
                x = (i % self.h_parts) * width
                y = (i / self.h_parts) * height
                #image_part = self.image.copy(x, y, width, height)
                inputs = []
                for pix_y in xrange(height):
                    for pix_x in xrange(width):
                        pix_rgb = QColor.fromRgbF(0.0,0.0,0.0)
                        if x + pix_x < self.image.width() and y + pix_y < self.image.height():
                            pix_rgb = QColor(self.image.pixel(x + pix_x, y + pix_y))
                        inputs.append(pix_rgb.redF())
                        inputs.append(pix_rgb.greenF())
                        inputs.append(pix_rgb.blueF())
                nn.learn(
                    [
                        [inputs, inputs]
                    ], self.max_error
                )
                error += nn.error
                progress = int(math.floor(i_count * 20 + float(i * 20) / self.nn_count))
                self.progress_changed.emit(progress)
            #print(error)
            if error <= self.max_error: iteration = False
            i_count += 1
        for i in xrange(self.nn_count):
            x = (i % self.h_parts) * width
            y = (i / self.h_parts) * height
            inputs = []
            for pix_y in xrange(height):
                for pix_x in xrange(width):
                    pix_rgb = QColor.fromRgbF(0.0,0.0,0.0)
                    if x + pix_x < self.image.width() and y + pix_y < self.image.height():
                        pix_rgb = QColor(self.image.pixel(x + pix_x, y + pix_y))
                    inputs.append(pix_rgb.redF())
                    inputs.append(pix_rgb.greenF())
                    inputs.append(pix_rgb.blueF())
            nn.calculate(inputs)
            c.append(nn.get_compressed_data())
            progress = int(math.floor(60 + float(i * 20) / self.nn_count))
            self.progress_changed.emit(progress)
        wei = open('weights','w')
        comp = open('comp', 'w')
        w = nn.get_decompress_weights()
        for line in w:
            wei.write(':'.join([str(x) for x in line]) + '\n')
        min_c = min([min(line) for line in c])
        max_c = max([max(line) for line in c])
        new_c = []
        for line in c:
            new_c.append([])
            for number in line:
                new_c[-1].append(chr(int(round((number - min_c) / (max_c - min_c) * 255))))
        c = new_c
        comp.write(':'.join([str(self.image.width()), str(self.image.height()), str(width), str(height), str(min_c), str(max_c)]) + '\n')
        for line in c:
            comp.write(''.join([str(x) for x in line]))
        comp.close()
        wei.close()
        nn = generate((len(w[0]), len(w)))
        nn.set_decompress_weights(w)
        for i in xrange(len(c)):
            x = (i % self.h_parts) * width
            y = (i / self.h_parts) * height
            inputs = []
            line = c[i]
            inputs = list([min_c + float(ord(z)) / 255 * (max_c - min_c)  for z in line])
            #inputs = line
            outputs = nn.calculate(inputs)
            for j in xrange(0, len(outputs), 3):
                pix_x = x + (j / 3) % width
                pix_y = y + (j / 3) / width
                if pix_x >= self.image.width(): continue
                if pix_y >= self.image.height(): continue                    #print 'new: j = %d, width = %d x = %d, y = %d' % (j, width, pix_x, pix_y)
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
            progress = int(math.floor(80 + float(i * 20) / self.nn_count))
            self.progress_changed.emit(progress)
        self.progress_complete.emit(new_image)

class MWindow(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.ui = Ui_MWindow()
        self.ui.setupUi(self)
        
        self.ui.btn_load_image.clicked.connect(self.load_image_clicked)
        self.ui.btn_next1.clicked.connect(self.next_clicked)
        self.ui.btn_back2.clicked.connect(self.back_clicked)
        self.ui.btn_next2.clicked.connect(self.process)
        
    def load_image_clicked(self):
        image_path = QFileDialog.getOpenFileName(self, u'Изображение', '.', u'Изображения (*.jpg *.png *.bmp)')
        if not image_path.isNull():
            image_path = unicode(image_path)
            self.image = QImage(image_path)
            self.ui.txt_h_parts.setValue(int(math.ceil(float(self.image.width()) / 1)))
            self.ui.txt_v_parts.setValue(int(math.ceil(float(self.image.height()) / 1)))
            self.ui.txt_max_error.setValue(25)
            self.ui.txt_zip.setValue(3)
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
        self.thread.inputs = int(math.ceil(float(self.image.width()) / self.ui.txt_h_parts.value()) * math.ceil(float(self.image.height()) / self.ui.txt_v_parts.value()) * 3)
        self.thread.hidden = int(self.ui.txt_zip.value())
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
        new_image.save('out.bmp')
        self.image.save('in.bmp')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MWindow()
    window.show()
    app.exec_()