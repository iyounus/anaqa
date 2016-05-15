import sys
from re import match
from os.path import expanduser
from PyQt4 import QtCore, QtGui

from reportlab.graphics.barcode import qr
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)

except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class AnaqaApp(QtGui.QMainWindow):

    def __init__(self):
        super(AnaqaApp, self).__init__()
        self.main_window()
        self.setup_form()
        self.setup_buttons()
        self.message_box()

    def main_window(self):
        self.setGeometry(50, 50, 650, 450)
        self.setWindowTitle("Anaqa Product Label Creater")
        self.setWindowIcon(QtGui.QIcon('anaqa_logo.png'))

        logo = QtGui.QLabel(self)
        logo.setGeometry(QtCore.QRect(370, 0, 270, 86))
        logo.setText(_fromUtf8(""))
        logo.setPixmap(QtGui.QPixmap(_fromUtf8("anaqa_logo_and_name.png")))
        logo.setObjectName(_fromUtf8("logo"))

    def setup_form(self):
        self.ref_box = self.input_box(30, 80, "prodRef", "Product Reference")
        self.name_box = self.input_box(30, 2*80, "prodName", "Product Name")
        self.type_box = self.input_box(30, 3*80, "prodType", "Product Type")
        self.lot_box = self.input_box(30, 4*80, "prodLot", "Lot Number")

    def setup_buttons(self):
        createBtn = QtGui.QPushButton(self)
        createBtn.setGeometry(QtCore.QRect(390, 350, 114, 35))
        createBtn.setObjectName(_fromUtf8("createButton"))
        createBtn.setText(_fromUtf8("Create"))
        createBtn.clicked.connect(self.create_click)

        closeBtn = QtGui.QPushButton(self)
        closeBtn.setGeometry(QtCore.QRect(510, 350, 114, 35))
        closeBtn.setObjectName(_fromUtf8("closeButton"))
        closeBtn.setText(_fromUtf8("Close"))
        closeBtn.clicked.connect(self.close)

    def input_box(self, x, y, name, title):
        H, W = 35, 300
        label = QtGui.QLabel(self)
        label.setGeometry(QtCore.QRect(x, y, W, H))
        label.setObjectName(_fromUtf8(name+"Label"))
        label.setText(_fromUtf8(title))

        line_edit = QtGui.QLineEdit(self)
        line_edit.setGeometry(QtCore.QRect(x, y+30, W, H))
        line_edit.setObjectName(_fromUtf8(name+"Input"))
        return line_edit

    def message_box(self):
        self.message = QtGui.QLabel(self)
        self.message.setGeometry(QtCore.QRect(30, 5*80, 590, 35))
        self.message.setObjectName(_fromUtf8("messageLabel"))

    def create_click(self):
        self.prod_ref = str(self.ref_box.text())
        self.prod_name = str(self.name_box.text())
        self.prod_type = str(self.type_box.text())
        self.prod_lot = str(self.lot_box.text())
        if self.bad_input():
            return

        self.out_file_name()
        self.create_prod_labels()

    def bad_input(self):
        if not match("\d{6}[A-Z]{2}", self.prod_ref):
            self.message.setText("invalid product ref")
            return True
        if self.prod_name == "":
            self.message.setText("invalid product name")
            return True
        if not match("\d{6}", self.prod_lot):
            self.message.setText("invalid lot number")
            return True
        return False

    def create_prod_labels(self):
        """
        These values should be measured from the printed page.
        In all the following calculations, the bottom left corner of
        the page is considered to be at the origin of the x-y plane.
        All the coordinates should be provided w.r.t. the this origin.
        """
        # page size
        page_H = 297*mm  # A4
        page_W = 210*mm   # A4
        # coordinates of lower left corner of single label w.r.t. origin
        box_X = 15.5*mm
        box_Y = 6.1*mm
        # distance between rows and columns of labels
        box_X_shift = 46.2*mm
        box_Y_shift = 36.0*mm

        pdfmetrics.registerFont(TTFont('Arial', 'ARIALN.TTF'))
        c = Canvas(self.outFile)
        c.setLineWidth(0.1)

        # horizontal lines
        for i in range(7):
            c.line(39*mm + i*box_Y_shift, 10*mm,
                   39*mm + i*box_Y_shift, page_W-10*mm)
        # vertical lines
        for i in range(3):
            c.line(2*mm, 57*mm + i*box_X_shift,
                   page_H-2*mm, 57*mm + i*box_X_shift)

        for i in range(4):
            dx = box_X + i*box_X_shift
            for j in range(8):
                dy = box_Y + j*box_Y_shift
                self.draw_single_label(dy, dx, c)

        c.setPageRotation(90)
        c.setPageSize((page_W, page_H))
        c.save()
        self.message.setText("Creating " + self.outFile)

    def out_file_name(self):
        self.cdir = expanduser("~/Documents")
        self.outFile \
            = self.cdir + "/" + self.prod_ref + "_" + self.prod_lot + ".pdf"
        print self.outFile

    def prod_name_rows(self):
        rows = []
        row = ''
        for word in self.prod_name.split():
            if len(row + word) > 20:
                rows.append(row.strip())
                row = ''
            row += word + ' '

        rows.append(row.strip())
        if len(rows) > 3:
            rows = rows[:3]
            rows.append(self.prod_type)
        else:
            rows.append(self.prod_type)

        return rows

    def qr_code_gen(self):
        H, W = 13*mm, 13*mm

        qr_code = qr.QrCodeWidget("Anaqa")
        qr_code.addData(unicode(":" + self.prod_name))
        qr_code.addData(unicode(":" + self.prod_type))
        qr_code.addData(unicode(":" + self.prod_ref))
        qr_code.addData(unicode(":" + self.prod_lot))
        qr_code.barHeight = H
        qr_code.barWidth = W
        qr_draw = Drawing()
        qr_draw.add(qr_code)
        return qr_draw

    def draw_single_label(self, dx, dy, canvas):
        # these values are w.r.t the box
        # coordinates of bottom left corner of the qrcode w.r.t to box
        qr_X = 16*mm
        qr_Y = 3*mm
        renderPDF.draw(self.qr_code_gen(), canvas, qr_X + dx, qr_Y + dy)

        canvas.setFont("Arial", 6.5)
        canvas.drawString(1.2*mm + dx, 7.5*mm + dy, "REF")
        canvas.drawString(5.7*mm + dx, 7.5*mm + dy, self.prod_ref)
        canvas.drawString(1.2*mm + dx, 5.0*mm + dy, "LOT")
        canvas.drawString(5.7*mm + dx, 5.0*mm + dy, self.prod_lot)

        canvas.setFont("Arial", 10)
        text = self.prod_name_rows()
        for i, row in enumerate(text):
            canvas.drawString(1*mm + dx, 30.0*mm - i*4*mm + dy, row)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = AnaqaApp()
    myapp.show()
    sys.exit(app.exec_())
