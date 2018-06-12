# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'checkforupdates.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CheckForUpdates(object):
    def setupUi(self, CheckForUpdates):
        CheckForUpdates.setObjectName("CheckForUpdates")
        CheckForUpdates.resize(640, 250)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(CheckForUpdates)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(CheckForUpdates)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout.setObjectName("formLayout")
        self.labelCheckManual = QtWidgets.QLabel(self.groupBox)
        self.labelCheckManual.setOpenExternalLinks(True)
        self.labelCheckManual.setObjectName("labelCheckManual")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.labelCheckManual)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(1, QtWidgets.QFormLayout.FieldRole, spacerItem)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setText("")
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.labelCurrentVersion = QtWidgets.QLabel(self.groupBox)
        self.labelCurrentVersion.setObjectName("labelCurrentVersion")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.labelCurrentVersion)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setText("")
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.labelLatestVersion = QtWidgets.QLabel(self.groupBox)
        self.labelLatestVersion.setOpenExternalLinks(True)
        self.labelLatestVersion.setObjectName("labelLatestVersion")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.labelLatestVersion)
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtWidgets.QDialogButtonBox(CheckForUpdates)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(CheckForUpdates)
        self.buttonBox.clicked['QAbstractButton*'].connect(CheckForUpdates.accept)
        QtCore.QMetaObject.connectSlotsByName(CheckForUpdates)

    def retranslateUi(self, CheckForUpdates):
        _translate = QtCore.QCoreApplication.translate
        CheckForUpdates.setWindowTitle(_translate("CheckForUpdates", "About Buildertron..."))
        self.labelCheckManual.setText(_translate("CheckForUpdates", "Check Releases Manually"))
        self.label.setText(_translate("CheckForUpdates", "Current Version:"))
        self.labelCurrentVersion.setText(_translate("CheckForUpdates", "v0.0.0"))
        self.label_5.setText(_translate("CheckForUpdates", "Latest Version:"))
        self.labelLatestVersion.setText(_translate("CheckForUpdates", "vX.X.X"))

