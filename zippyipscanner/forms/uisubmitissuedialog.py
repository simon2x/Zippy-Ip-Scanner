# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'submitissuedialog.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SubmitIssueDialog(object):
    def setupUi(self, SubmitIssueDialog):
        SubmitIssueDialog.setObjectName("SubmitIssueDialog")
        SubmitIssueDialog.resize(640, 250)
        self.gridLayout = QtWidgets.QGridLayout(SubmitIssueDialog)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 1, 1, 1)
        self.label = QtWidgets.QLabel(SubmitIssueDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(SubmitIssueDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(SubmitIssueDialog)
        self.label_4.setOpenExternalLinks(True)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 1, 1, 1)

        self.retranslateUi(SubmitIssueDialog)
        self.buttonBox.accepted.connect(SubmitIssueDialog.accept)
        self.buttonBox.rejected.connect(SubmitIssueDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SubmitIssueDialog)

    def retranslateUi(self, SubmitIssueDialog):
        _translate = QtCore.QCoreApplication.translate
        SubmitIssueDialog.setWindowTitle(_translate("SubmitIssueDialog", "Submit an issue..."))
        self.label.setText(_translate("SubmitIssueDialog", "Buildertron Issues:"))
        self.label_4.setText(_translate("SubmitIssueDialog", "https://github.com/swprojects/Buildertron/issues"))

