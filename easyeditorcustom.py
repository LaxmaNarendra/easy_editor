from PyQt5.QtWidgets import (
  QApplication,
  QWidget,
  QPushButton,
  QVBoxLayout,
  QHBoxLayout,
  QLabel,
  QListWidget,
  QFileDialog,
  QDialog,
  QDialogButtonBox,
  QScrollArea,
  QRubberBand,
)
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtCore import Qt, QRect, QPoint, QSize
import os
from PIL import Image


class CropLabel(QLabel):
  def __init__(self):
    super().__init__()
    self.setCursor(QCursor(Qt.CrossCursor))
    self.start_point = QPoint()
    self.end_point = QPoint()
    self.is_selecting = False
    self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)

  def mousePressEvent(self, event):
    if event.button() == Qt.LeftButton:
      self.start_point = event.pos()
      self.rubber_band.setGeometry(QRect(self.start_point, QSize()))
      self.rubber_band.show()
      self.is_selecting = True

  def mouseMoveEvent(self, event):
    if self.is_selecting:
      self.rubber_band.setGeometry(
        QRect(self.start_point, event.pos()).normalized()
      )

  def mouseReleaseEvent(self, event):
    if event.button() == Qt.LeftButton and self.is_selecting:
      self.end_point = event.pos()
      self.rubber_band.setGeometry(
        QRect(self.start_point, self.end_point).normalized()
      )
      self.is_selecting = False

  def getCropRect(self):
    return self.rubber_band.geometry()


class CropDialog(QDialog):
  def __init__(self, image_path, parent=None):
    super().__init__(parent)
    self.setWindowTitle('Crop Image - Drag to select area')
    self.resize(750, 620)

    self.original_pixmap = QPixmap(image_path)
    scaled_pixmap = self.original_pixmap.scaled(
      680, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation
    )
    self.scale_x = self.original_pixmap.width() / scaled_pixmap.width()
    self.scale_y = self.original_pixmap.height() / scaled_pixmap.height()

    self.crop_label = CropLabel()
    self.crop_label.setPixmap(scaled_pixmap)
    self.crop_label.setFixedSize(scaled_pixmap.size())

    scroll = QScrollArea()
    scroll.setWidget(self.crop_label)
    scroll.setAlignment(Qt.AlignCenter)

    hint = QLabel('Klik dan seret pada gambar untuk memilih area crop')
    hint.setAlignment(Qt.AlignCenter)
    hint.setStyleSheet('color: gray; font-style: italic;')

    buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    buttons.accepted.connect(self.accept)
    buttons.rejected.connect(self.reject)

    layout = QVBoxLayout()
    layout.addWidget(hint)
    layout.addWidget(scroll)
    layout.addWidget(buttons)
    self.setLayout(layout)

  def getCropBox(self):
    rect = self.crop_label.getCropRect()
    if rect.isNull() or rect.width() == 0 or rect.height() == 0:
      return None
    x = int(rect.x() * self.scale_x)
    y = int(rect.y() * self.scale_y)
    w = int(rect.width() * self.scale_x)
    h = int(rect.height() * self.scale_y)
    return (x, y, x + w, y + h)


app = QApplication([])
win = QWidget()
win.setWindowTitle('Easy Editor')
win.resize(700, 500)

#daftar widget
btndirectory = QPushButton('Folder')
listfiles = QListWidget()
label = QLabel('Image')
btnleft = QPushButton('Left')
btnright = QPushButton('Right')
btnmirror = QPushButton('Mirror')
btnsharpen = QPushButton('Sharpness')
btnbnw = QPushButton('B&W')
btncrop = QPushButton('Crop')

#layout
row = QHBoxLayout()
col1 = QVBoxLayout()
col2 = QVBoxLayout()

col1.addWidget(btndirectory)
col1.addWidget(listfiles)

col21 = QHBoxLayout()
col22 = QHBoxLayout()

col21.addWidget(label)

col22.addWidget(btnleft)
col22.addWidget(btnright)
col22.addWidget(btnmirror)
col22.addWidget(btnsharpen)
col22.addWidget(btnbnw)
col22.addWidget(btncrop)

#gabung layout
col2.addLayout(col21)
col2.addLayout(col22)

row.addLayout(col1, 20)
row.addLayout(col2, 80)

win.setLayout(row)

win.show()

workdir = ''
def filter(files, extensions):
  result = []
  for filename in files:
    for ext in extensions:
      if filename.endswith(ext):
        result.append(filename)
  return result

def chooseWorkdir():
  global workdir
  workdir = QFileDialog.getExistingDirectory()

def showFilenamesList():
  extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp', '.svg']
  chooseWorkdir()
  filenames = filter(os.listdir(workdir), extensions)
  listfiles.clear()
  for filename in filenames:
    listfiles.addItem(filename)

btndirectory.clicked.connect(showFilenamesList)

class ImageProcessor:
  def __init__(self):
    self.image = None
    self.direktori = None
    self.filename = None
    self.save_dir = 'modifikasi/'

  def loadImage(self, direktori, filename):
    self.direktori = direktori
    self.filename = filename
    image_path = os.path.join(direktori, filename)
    self.image = Image.open(image_path)

  def showImage(self, path):
    label.hide()
    pixmapimage = QPixmap(path)
    w, h = label.width(), label.height()
    pixmapimage = pixmapimage.scaled(w, h, Qt.KeepAspectRatio)
    label.setPixmap(pixmapimage)
    label.show()

  def saveImage(self):
    path = os.path.join(self.direktori, self.save_dir)
    if not os.path.exists(path):
      os.mkdir(path)
    save_path = os.path.join(path, self.filename)
    self.image.save(save_path)

  def do_bw(self):
    self.image = self.image.convert('L')
    self.saveImage()
    imagepath = os.path.join(self.direktori, self.save_dir, self.filename)
    self.showImage(imagepath)

  def do_left(self):
    self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)
    self.saveImage()
    imagepath = os.path.join(self.direktori, self.save_dir, self.filename)
    self.showImage(imagepath)

  def do_right(self):
    self.image = self.image.transpose(Image.FLIP_RIGHT_LEFT)
    self.saveImage()
    imagepath = os.path.join(self.direktori, self.save_dir, self.filename)
    self.showImage(imagepath)

  def do_crop(self):
    if self.image is None:
      return
    imagepath = os.path.join(self.direktori, self.filename)
    dialog = CropDialog(imagepath)
    if dialog.exec_() == QDialog.Accepted:
      crop_box = dialog.getCropBox()
      if crop_box:
        self.image = self.image.crop(crop_box)
        self.saveImage()
        imagepath = os.path.join(self.direktori, self.save_dir, self.filename)
        self.showImage(imagepath)

workimage = ImageProcessor()

def showChosenImage():
  if listfiles.currentRow() >= 0:
    filename = listfiles.currentItem().text()
    workimage.loadImage(workdir, filename)
    imagepath = os.path.join(workdir, filename)
    workimage.showImage(imagepath)

listfiles.currentRowChanged.connect(showChosenImage)
btnbnw.clicked.connect(workimage.do_bw)
btnleft.clicked.connect(workimage.do_left)
btncrop.clicked.connect(workimage.do_crop)

app.exec_()
