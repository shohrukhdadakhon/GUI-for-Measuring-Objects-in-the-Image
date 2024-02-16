import sys

from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QRegExpValidator
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import cv2, imutils
import numpy as np

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        uic.loadUi('design1.ui', self)

        self.setWindowTitle("Object size measurement")
        self.label_image.setStyleSheet("background-color: lightgrey")
        self.lineEdit_width.setPlaceholderText("Width")


        regex = QRegExp("^\d{1,5}$|(?=^.{1,20}$)^\d+\.\d{0,3}$")
        validator = QRegExpValidator(regex)
        self.lineEdit_width.setValidator(validator)
        self.line_min.setValidator(validator)
        self.line_max.setValidator(validator)
        self.imagepath = ''
        self.btn_image.clicked.connect(self.loadImage)
        self.btn_detect.clicked.connect(self.detect)


        self.UiComponents()

        self.show()

    def loadImage(self):
        self.imagepath = QFileDialog.getOpenFileName(None, 'OpenFile', '')[0]
        pixmap = QPixmap(self.imagepath)

        aspectratio_pixmap = pixmap.scaled(1542, 981, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.label_image.setPixmap(aspectratio_pixmap)


    def detect(self):
        if self.imagepath != '' and self.lineEdit_width.text() != '':

            # load the image, convert it to grayscale, and blur it slightly
            image = cv2.imread(self.imagepath)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (7, 7), 0)

            # perform edge detection, then perform a dilation + erosion to
            # close gaps in between object edges
            edged = cv2.Canny(gray, 50, 100)
            edged = cv2.dilate(edged, None, iterations=1)
            edged = cv2.erode(edged, None, iterations=1)

            # find contours in the edge map
            cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)

            # sort the contours from left-to-right and initialize the
            # 'pixels per metric' calibration variable
            (cnts, _) = contours.sort_contours(cnts)
            pixelsPerMetric = None

            count = 0
            for c in cnts:
                # if the contour is not sufficiently large, ignore it
                if cv2.contourArea(c) < float(self.line_min.text()) or cv2.contourArea(c) > float(self.line_max.text()):
                    continue
                count += 1

                # compute the rotated bounding box of the contour
                orig = image.copy()
                box = cv2.minAreaRect(c)
                box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
                box = np.array(box, dtype="int")

                # order the points in the contour such that they appear
                # in top-left, top-right, bottom-right, and bottom-left
                # order, then draw the outline of the rotated bounding
                # box
                box = perspective.order_points(box)
                cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

                # loop over the original points and draw them
                for (x, y) in box:
                    cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

                # unpack the ordered bounding box, then compute the midpoint
                # between the top-left and top-right coordinates, followed by
                # the midpoint between bottom-left and bottom-right coordinates
                (tl, tr, br, bl) = box
                (tltrX, tltrY) = (((tl[0] + tr[0]) * 0.5), ((tl[1] + tr[1]) * 0.5))
                (blbrX, blbrY) = (((bl[0] + br[0]) * 0.5), ((bl[1] + br[1]) * 0.5))

                # compute the midpoint between the top-left and top-right points,
                # followed by the midpoint between the top-righ and bottom-right
                (tlblX, tlblY) = (((tl[0] + bl[0]) * 0.5), ((tl[1] + bl[1]) * 0.5))
                (trbrX, trbrY) = (((tr[0] + br[0]) * 0.5), ((tr[1] + br[1]) * 0.5))

                # draw the midpoints on the image
                cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
                cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
                cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
                cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

                # draw lines between the midpoints
                cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
                         (255, 0, 255), 2)
                cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
                         (255, 0, 255), 2)

                # compute the Euclidean distance between the midpoints
                dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
                dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

                # if the pixels per metric has not been initialized, then
                # compute it as the ratio of pixels to supplied metric
                inputWidth = self.lineEdit_width.text()

                if pixelsPerMetric is None:
                    pixelsPerMetric = dB / float(inputWidth)

                # compute the size of the object
                dimA = dB / pixelsPerMetric
                dimB = dA / pixelsPerMetric

                # draw the object sizes on the image
                cv2.putText(orig, ("{:.3f}" + self.comboBox_width.currentText()).format(dimA),
                            (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
                            0.65, (255, 255, 255), 2)
                cv2.putText(orig, ("{:.3f}" + self.comboBox_width.currentText()).format(dimB),
                            (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
                            0.65, (255, 255, 255), 2)
                self.label_cnt.setText("Objects Detected: " + str(count))

                cv2.imshow("Image", orig)
                cv2.waitKey(0)

        elif self.imagepath == '':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Please select an image")
            msg.setInformativeText('You need to select an image')
            msg.setWindowTitle("Error")
            msg.exec_()
        elif self.lineEdit_width.text() == '':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Please enter width")
            msg.setInformativeText('You need to enter the width of the left most object')
            msg.setWindowTitle("Error")
            msg.exec_()

    def UiComponents(self):
        self.showMaximized()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    ui = MainWindow()
    ui.show()

    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Closing Window')
