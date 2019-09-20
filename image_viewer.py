from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from url_parser import IsValidUrl

from os import path, sep
import urllib.request


# TODO: https://forum.qt.io/topic/100381/allow-qgraphicsview-to-move-outside-scene/2
# source: https://stackoverflow.com/questions/35508711/how-to-enable-pan-and-zoom-in-a-qgraphicsview
class ImageViewer(QGraphicsView):
    photoClicked = pyqtSignal(QPoint)

    def __init__(self, parent):
        super().__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self._photo = QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(25, 25, 25)))
        self.setFrameShape(QFrame.NoFrame)
        self.setFocusPolicy(Qt.NoFocus)
        
    def removePhoto(self):
        self._empty = True
        self.setDragMode(QGraphicsView.NoDrag)
        self._photo.setPixmap(QPixmap())

    def hasPhoto(self):
        return not self._empty

    # TODO: this doesn't actually do anything right now when set to False, oof
    #  should reset the zoom
    def fitInView(self, scale=False, scale_down=True):
        rect = QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                
                if scale:
                    factor = min(viewrect.width() / scenerect.width(),
                                 viewrect.height() / scenerect.height())
                    self.scale(factor, factor)
                    
                elif scale_down:
                    w_factor = 1.0
                    h_factor = 1.0
                    
                    if scenerect.width() > viewrect.width():
                        w_factor = viewrect.width() / scenerect.width()

                    if scenerect.height() > viewrect.height():
                        h_factor = viewrect.height() / scenerect.height()
                        
                    factor = min(w_factor, h_factor)
                    self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, image_name):
        if IsValidUrl(image_name):
            pixmap = QPixmapFromURL(image_name)
        else:
            pixmap = QPixmap(image_name)
            
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
            self.fitInView(False)
            return True
        else:
            self.removePhoto()
            print("Image doesn't exist: " + image_name)
            return False

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
                
            self.scale(factor, factor)
            
            return
            
            # TODO: fix this code, it's broken
                
            # check if we are close to the native resolution, if so, go that
            # or adjust to the viewport size if it's closer to that
            rect = QRectF(self._photo.pixmap().rect())
            scenerect = self.transform().mapRect(rect)
            viewrect = self.viewport().rect()
            
            dist_needed = 200
            
            try:
                current_width, current_height = int(scenerect.width()), int(scenerect.height())
                image_width, image_height = int(rect.width()), int(rect.height())
                view_width, view_height = int(viewrect.width()), int(viewrect.height())

                # these are broken
                '''
                if current_height in range(view_height - dist_needed, view_height + dist_needed):
                    print("cool2")
                    factor = view_height / current_height
                    self.scale(factor, factor)
                    
                elif current_width in range(view_width - dist_needed, view_width + dist_needed):
                    print("cool")
                    factor = view_width / current_width
                    self.scale(factor, factor)
                '''

                if current_height in range(image_height - dist_needed, image_height + dist_needed):
                    print("cool2")
                    factor = image_height / current_height
                    self.scale(factor, factor)
                    
                elif current_width in range(image_width - dist_needed, image_width + dist_needed):
                    print("cool")
                    factor = image_width / current_width
                    self.scale(factor, factor)

            except Exception as F:
                print(str(F))

    def toggleDragMode(self):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            self.photoClicked.emit(QPoint(event.pos()))
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        parent = self.parent()

        try:
            image_list = parent.GetImageList()
            current_image = parent.GetCurrentImage()
            
            if image_list:
                image_list_len = len(image_list) - 1
                if image_list_len == 0:
                    return
                
                current_image_index = image_list.index(current_image)
                key = event.key()
                add_image_index = 1
                
                while True:
                    if key == Qt.Key_Left:
                        next_image = current_image_index - add_image_index
                    elif key == Qt.Key_Right:
                        next_image = current_image_index + add_image_index
                    else:
                        return
                    
                    if image_list_len >= next_image:
                        if self.setPhoto(image_list[next_image]):
                            parent._current_image = next_image
                            break
                        else:
                            add_image_index += 1
                            continue
                        
                    elif image_list_len == current_image_index:
                        current_image_index = -1
                        continue
                        
                    else:
                        self.removePhoto()
                        break
            
        except Exception as F:
            print(str(F))
        

def QPixmapFromURLOld(url):
    data = urllib.request.urlopen(url).read()
    pixmap = QPixmap()
    pixmap.loadFromData(data)
    return pixmap
    

def QPixmapFromURL(url):
    try:
        image_base_name = str(path.basename(url).split("?", 1)[0])
        image_path = "images" + sep + image_base_name
        if not path.isfile(image_path):
            data = urllib.request.urlopen(url).read()
            with open(image_path, "wb") as image_file:
                image_file.write(data)
            pixmap = QPixmap()
            pixmap.loadFromData(data)
        else:
            pixmap = QPixmap(image_path)
        return pixmap
    
    except Exception as F:
        print(str(F))
    

def QImageFromURL(url):
    data = urllib.request.urlopen(url).read()
    image = QImage()
    image.loadFromData(data)
    return image


def QPixmapAndQImageFromURL(url):
    data = urllib.request.urlopen(url).read()
    qpixmap = QPixmap()
    qpixmap.loadFromData(data)
    qimage = QImage()
    qimage.loadFromData(data)
    return qimage, qpixmap

