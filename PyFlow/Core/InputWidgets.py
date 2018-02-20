import weakref
from Qt import QtCore
from Qt import QtGui
from Qt.QtWidgets import QDoubleSpinBox
from Qt.QtWidgets import QSpinBox
from Qt.QtWidgets import QWidget
from Qt.QtWidgets import QSpacerItem
from Qt.QtWidgets import QPushButton
from Qt.QtWidgets import QLineEdit
from Qt.QtWidgets import QCheckBox
from Qt.QtWidgets import QGraphicsProxyWidget
from Qt.QtWidgets import QGridLayout
from Qt.QtWidgets import QHBoxLayout
from Qt.QtWidgets import QSizePolicy
from AGraphCommon import *
from AbstractGraph import PinBase
from .. import FloatVector3InputWidget_ui
from .. import FloatVector4InputWidget_ui
from .. import Matrix33InputWidget_ui
from .. import Matrix44InputWidget_ui
import pyrr


def _configDoubleSpinBox(sb):
    sb.setRange(FLOAT_RANGE_MIN, FLOAT_RANGE_MAX)
    sb.setSingleStep(FLOAT_SINGLE_STEP)
    sb.setDecimals(FLOAT_DECIMALS)


def _configIntSpinBox(sb):
    sb.setRange(INT_RANGE_MIN, INT_RANGE_MAX)


class InputWidgetRaw(QWidget):
    """
    This type of widget can be used as a base class for complex ui generated by designer
    """
    def __init__(self, parent=None, dataSetCallback=None, defaultValue=None, **kwds):
        super(InputWidgetRaw, self).__init__(parent=parent, **kwds)
        self._defaultValue = defaultValue
        # fuction with signature void(object)
        # this will set data to pin
        self.dataSetCallback = dataSetCallback

    def onResetValue(self):
        self.setWidgetValue(self._defaultValue)

    def setWidgetValue(self, value):
        '''to widget'''
        pass

    def widgetValueUpdated(self, value):
        '''from widget'''
        pass


class InputWidgetSingle(InputWidgetRaw):
    """
    This type of widget is used for a simple widgets like buttons, checkboxes etc.
    It consists of horizontal layout widget itself and reset button.
    """

    def __init__(self, parent=None, dataSetCallback=None, defaultValue=None, **kwds):
        super(InputWidgetSingle, self).__init__(parent=parent, dataSetCallback=dataSetCallback, defaultValue=defaultValue, **kwds)
        # from widget
        self.bWidgetSet = False
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setSpacing(1)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pbReset = QPushButton(self)
        self.pbReset.setMaximumSize(QtCore.QSize(25, 25))
        self.pbReset.setText("")
        self.pbReset.setObjectName("pbReset")
        self.pbReset.setIcon(QtGui.QIcon(":/icons/resources/reset.png"))
        self.horizontalLayout.addWidget(self.pbReset)
        self.pbReset.clicked.connect(self.onResetValue)

        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self._index = 0

    def setWidget(self, widget):
        self.horizontalLayout.insertWidget(self._index, widget)


class ExecInputWidget(InputWidgetSingle):
    """docstring for ExecInputWidget"""
    def __init__(self, parent=None, **kwds):
        super(ExecInputWidget, self).__init__(parent=parent, **kwds)
        self.pb = QPushButton('execute', self)
        self.setWidget(self.pb)
        self.pb.clicked.connect(self.dataSetCallback)
        self.pbReset.deleteLater()


class FloatInputWidget(InputWidgetSingle):
    """
    Floating point data input widget
    """

    def __init__(self, parent=None, **kwds):
        super(FloatInputWidget, self).__init__(parent=parent, **kwds)
        self.sb = QDoubleSpinBox(self)
        _configDoubleSpinBox(self.sb)
        self.setWidget(self.sb)
        # when spin box updated call setter function
        self.sb.valueChanged.connect(lambda val: self.dataSetCallback(val))

    def setWidgetValue(self, val):
        self.sb.setValue(float(val))


class IntInputWidget(InputWidgetSingle):
    """
    Decimal number input widget
    """
    def __init__(self, parent=None, **kwds):
        super(IntInputWidget, self).__init__(parent=parent, **kwds)
        self.sb = QSpinBox(self)
        _configIntSpinBox(self.sb)
        self.setWidget(self.sb)
        self.sb.valueChanged.connect(lambda val: self.dataSetCallback(val))

    def setWidgetValue(self, val):
        self.sb.setValue(int(val))


class StringInputWidget(InputWidgetSingle):
    """
    String data input widget
    """
    def __init__(self, parent=None, **kwds):
        super(StringInputWidget, self).__init__(parent=parent, **kwds)
        self.le = QLineEdit(self)
        self.le.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.setWidget(self.le)
        self.le.textChanged.connect(lambda val: self.dataSetCallback(val))

    def setWidgetValue(self, val):
        self.le.setText(str(val))


class BoolInputWidget(InputWidgetSingle):
    """Boolean data input widget"""
    def __init__(self, parent=None, **kwds):
        super(BoolInputWidget, self).__init__(parent=parent, **kwds)
        self.cb = QCheckBox(self)
        self.setWidget(self.cb)
        self.cb.stateChanged.connect(lambda val: self.dataSetCallback(bool(val)))

    def setWidgetValue(self, val):
        if bool(val):
            self.cb.setCheckState(QtCore.Qt.Checked)
        else:
            self.cb.setCheckState(QtCore.Qt.Unchecked)


class FloatVector3InputWidget(InputWidgetRaw, FloatVector3InputWidget_ui.Ui_Form):
    """Vector3 data input widget"""
    def __init__(self, **kwds):
        super(FloatVector3InputWidget, self).__init__(**kwds)
        self.setupUi(self)
        self._configSpinBoxes()
        self.dsbX.valueChanged.connect(self._onDataChangedX)
        self.dsbY.valueChanged.connect(self._onDataChangedY)
        self.dsbZ.valueChanged.connect(self._onDataChangedZ)
        self.pbReset.clicked.connect(self.onResetValue)

    def asDataTypeClass(self):
        return pyrr.Vector3([self.dsbX.value(), self.dsbY.value(), self.dsbZ.value()])

    def _configSpinBoxes(self):
        self.dsbX.setDecimals(FLOAT_DECIMALS)
        self.dsbY.setDecimals(FLOAT_DECIMALS)
        self.dsbZ.setDecimals(FLOAT_DECIMALS)

        self.dsbX.setRange(FLOAT_RANGE_MIN, FLOAT_RANGE_MAX)
        self.dsbY.setRange(FLOAT_RANGE_MIN, FLOAT_RANGE_MAX)
        self.dsbZ.setRange(FLOAT_RANGE_MIN, FLOAT_RANGE_MAX)

        self.dsbX.setSingleStep(FLOAT_SINGLE_STEP)
        self.dsbY.setSingleStep(FLOAT_SINGLE_STEP)
        self.dsbZ.setSingleStep(FLOAT_SINGLE_STEP)

    def _onDataChangedX(self, val):
        v = self.asDataTypeClass()
        v.x = val
        self.dataSetCallback(v)

    def _onDataChangedY(self, val):
        v = self.asDataTypeClass()
        v.y = val
        self.dataSetCallback(v)

    def _onDataChangedZ(self, val):
        v = self.asDataTypeClass()
        v.z = val
        self.dataSetCallback(v)

    def setWidgetValue(self, val):
        self.dsbX.setValue(val.x)
        self.dsbY.setValue(val.y)
        self.dsbZ.setValue(val.z)


class FloatVector4InputWidget(InputWidgetRaw, FloatVector4InputWidget_ui.Ui_Form):
    """Vector4 data input widget"""
    def __init__(self, **kwds):
        super(FloatVector4InputWidget, self).__init__(**kwds)
        self.setupUi(self)
        self._configSpinBoxes()
        self.dsbX.valueChanged.connect(self._onDataChangedX)
        self.dsbY.valueChanged.connect(self._onDataChangedY)
        self.dsbZ.valueChanged.connect(self._onDataChangedZ)
        self.dsbW.valueChanged.connect(self._onDataChangedW)
        self.pbReset.clicked.connect(self.onResetValue)

    def asDataTypeClass(self):
        return pyrr.Vector4([self.dsbX.value(), self.dsbY.value(), self.dsbZ.value(), self.dsbW.value()])

    def _configSpinBoxes(self):
        self.dsbX.setRange(FLOAT_RANGE_MIN, FLOAT_RANGE_MAX)
        self.dsbY.setRange(FLOAT_RANGE_MIN, FLOAT_RANGE_MAX)
        self.dsbZ.setRange(FLOAT_RANGE_MIN, FLOAT_RANGE_MAX)
        self.dsbW.setRange(FLOAT_RANGE_MIN, FLOAT_RANGE_MAX)
        self.dsbX.setSingleStep(FLOAT_SINGLE_STEP)
        self.dsbY.setSingleStep(FLOAT_SINGLE_STEP)
        self.dsbZ.setSingleStep(FLOAT_SINGLE_STEP)
        self.dsbW.setSingleStep(FLOAT_SINGLE_STEP)
        self.dsbX.setDecimals(FLOAT_DECIMALS)
        self.dsbY.setDecimals(FLOAT_DECIMALS)
        self.dsbZ.setDecimals(FLOAT_DECIMALS)
        self.dsbW.setDecimals(FLOAT_DECIMALS)

    def _onDataChangedX(self, val):
        v = self.asDataTypeClass()
        v.x = val
        self.dataSetCallback(v)

    def _onDataChangedY(self, val):
        v = self.asDataTypeClass()
        v.y = val
        self.dataSetCallback(v)

    def _onDataChangedZ(self, val):
        v = self.asDataTypeClass()
        v.z = val
        self.dataSetCallback(v)

    def _onDataChangedW(self, val):
        v = self.asDataTypeClass()
        v.w = val
        self.dataSetCallback(v)

    def setWidgetValue(self, val):
        self.dsbX.setValue(val.x)
        self.dsbY.setValue(val.y)
        self.dsbZ.setValue(val.z)
        self.dsbW.setValue(val.w)


class QuatInputWidget(FloatVector4InputWidget):
    """Quaternion data input widget"""
    def __init__(self, **kwds):
        super(QuatInputWidget, self).__init__(**kwds)

    def asDataTypeClass(self):
        return pyrr.Quaternion([self.dsbX.value(), self.dsbY.value(), self.dsbZ.value(), self.dsbW.value()])


class Matrix33InputWidget(InputWidgetRaw, Matrix33InputWidget_ui.Ui_Form):
    """Matrix33 data input widget"""
    def __init__(self, parent=None, **kwds):
        super(Matrix33InputWidget, self).__init__(parent=parent, **kwds)
        self.setupUi(self)
        self._configSpinBoxes()

        self.dsbm11.valueChanged.connect(self.m11Changed)
        self.dsbm12.valueChanged.connect(self.m12Changed)
        self.dsbm13.valueChanged.connect(self.m13Changed)

        self.dsbm21.valueChanged.connect(self.m21Changed)
        self.dsbm22.valueChanged.connect(self.m22Changed)
        self.dsbm23.valueChanged.connect(self.m23Changed)

        self.dsbm31.valueChanged.connect(self.m31Changed)
        self.dsbm32.valueChanged.connect(self.m32Changed)
        self.dsbm33.valueChanged.connect(self.m33Changed)

        self.pbReset.clicked.connect(self.onResetValue)

    def asDataTypeClass(self):
        return pyrr.Matrix33([
            [self.dsbm11.value(), self.dsbm12.value(), self.dsbm13.value()],
            [self.dsbm21.value(), self.dsbm22.value(), self.dsbm23.value()],
            [self.dsbm31.value(), self.dsbm32.value(), self.dsbm33.value()]
        ])

    def _configSpinBoxes(self):
        ls = [self.dsbm11, self.dsbm12, self.dsbm13,
              self.dsbm21, self.dsbm22, self.dsbm23,
              self.dsbm31, self.dsbm32, self.dsbm33]
        for sb in ls:
            sb.setRange(FLOAT_RANGE_MIN, FLOAT_RANGE_MAX)
            sb.setSingleStep(FLOAT_SINGLE_STEP)
            sb.setDecimals(FLOAT_DECIMALS)

    def m11Changed(self, val):
        m = self.asDataTypeClass()
        m.m11 = val
        self.dataSetCallback(m)

    def m12Changed(self, val):
        m = self.asDataTypeClass()
        m.m12 = val
        self.dataSetCallback(m)

    def m13Changed(self, val):
        m = self.asDataTypeClass()
        m.m13 = val
        self.dataSetCallback(m)

    def m21Changed(self, val):
        m = self.asDataTypeClass()
        m.m21 = val
        self.dataSetCallback(m)

    def m22Changed(self, val):
        m = self.asDataTypeClass()
        m.m22 = val
        self.dataSetCallback(m)

    def m23Changed(self, val):
        m = self.asDataTypeClass()
        m.m23 = val
        self.dataSetCallback(m)

    def m31Changed(self, val):
        m = self.asDataTypeClass()
        m.m31 = val
        self.dataSetCallback(m)

    def m32Changed(self, val):
        m = self.asDataTypeClass()
        m.m32 = val
        self.dataSetCallback(m)

    def m33Changed(self, val):
        m = self.asDataTypeClass()
        m.m33 = val
        self.dataSetCallback(m)

    def setWidgetValue(self, val):
        self.dsbm11.setValue(val.m11)
        self.dsbm12.setValue(val.m12)
        self.dsbm13.setValue(val.m13)

        self.dsbm21.setValue(val.m21)
        self.dsbm22.setValue(val.m22)
        self.dsbm23.setValue(val.m23)

        self.dsbm31.setValue(val.m31)
        self.dsbm32.setValue(val.m32)
        self.dsbm33.setValue(val.m33)


class Matrix44InputWidget(InputWidgetRaw, Matrix44InputWidget_ui.Ui_Form):
    """Matrix44 data input widget"""
    def __init__(self, parent=None, **kwds):
        super(Matrix44InputWidget, self).__init__(parent=parent, **kwds)
        self.setupUi(self)
        self._configSpinBoxes()

        self.dsbm11.valueChanged.connect(self.m11Changed)
        self.dsbm12.valueChanged.connect(self.m12Changed)
        self.dsbm13.valueChanged.connect(self.m13Changed)
        self.dsbm14.valueChanged.connect(self.m14Changed)

        self.dsbm21.valueChanged.connect(self.m21Changed)
        self.dsbm22.valueChanged.connect(self.m22Changed)
        self.dsbm23.valueChanged.connect(self.m23Changed)
        self.dsbm24.valueChanged.connect(self.m24Changed)

        self.dsbm31.valueChanged.connect(self.m31Changed)
        self.dsbm32.valueChanged.connect(self.m32Changed)
        self.dsbm33.valueChanged.connect(self.m33Changed)
        self.dsbm34.valueChanged.connect(self.m34Changed)

        self.dsbm41.valueChanged.connect(self.m41Changed)
        self.dsbm42.valueChanged.connect(self.m42Changed)
        self.dsbm43.valueChanged.connect(self.m43Changed)
        self.dsbm44.valueChanged.connect(self.m44Changed)

        self.pbReset.clicked.connect(self.onResetValue)

    def asDataTypeClass(self):
        return pyrr.Matrix44([
            [self.dsbm11.value(), self.dsbm12.value(), self.dsbm13.value(), self.dsbm14.value()],
            [self.dsbm21.value(), self.dsbm22.value(), self.dsbm23.value(), self.dsbm24.value()],
            [self.dsbm31.value(), self.dsbm32.value(), self.dsbm33.value(), self.dsbm34.value()],
            [self.dsbm41.value(), self.dsbm42.value(), self.dsbm43.value(), self.dsbm44.value()]
        ])

    def _configSpinBoxes(self):
        ls = [self.dsbm11, self.dsbm12, self.dsbm13, self.dsbm14,
              self.dsbm21, self.dsbm22, self.dsbm23, self.dsbm24,
              self.dsbm31, self.dsbm32, self.dsbm33, self.dsbm34,
              self.dsbm41, self.dsbm42, self.dsbm43, self.dsbm44]
        for sb in ls:
            sb.setRange(FLOAT_RANGE_MIN, FLOAT_RANGE_MAX)
            sb.setSingleStep(FLOAT_SINGLE_STEP)
            sb.setDecimals(FLOAT_DECIMALS)

    def m11Changed(self, val):
        m = self.asDataTypeClass()
        m.m11 = val
        self.dataSetCallback(m)

    def m12Changed(self, val):
        m = self.asDataTypeClass()
        m.m12 = val
        self.dataSetCallback(m)

    def m13Changed(self, val):
        m = self.asDataTypeClass()
        m.m13 = val
        self.dataSetCallback(m)

    def m14Changed(self, val):
        m = self.asDataTypeClass()
        m.m14 = val
        self.dataSetCallback(m)

    def m21Changed(self, val):
        m = self.asDataTypeClass()
        m.m21 = val
        self.dataSetCallback(m)

    def m22Changed(self, val):
        m = self.asDataTypeClass()
        m.m22 = val
        self.dataSetCallback(m)

    def m23Changed(self, val):
        m = self.asDataTypeClass()
        m.m23 = val
        self.dataSetCallback(m)

    def m24Changed(self, val):
        m = self.asDataTypeClass()
        m.m24 = val
        self.dataSetCallback(m)

    def m31Changed(self, val):
        m = self.asDataTypeClass()
        m.m31 = val
        self.dataSetCallback(m)

    def m32Changed(self, val):
        m = self.asDataTypeClass()
        m.m32 = val
        self.dataSetCallback(m)

    def m33Changed(self, val):
        m = self.asDataTypeClass()
        m.m33 = val
        self.dataSetCallback(m)

    def m34Changed(self, val):
        m = self.asDataTypeClass()
        m.m34 = val
        self.dataSetCallback(m)

    def m41Changed(self, val):
        m = self.asDataTypeClass()
        m.m41 = val
        self.dataSetCallback(m)

    def m42Changed(self, val):
        m = self.asDataTypeClass()
        m.m42 = val
        self.dataSetCallback(m)

    def m43Changed(self, val):
        m = self.asDataTypeClass()
        m.m43 = val
        self.dataSetCallback(m)

    def m44Changed(self, val):
        m = self.asDataTypeClass()
        m.m44 = val
        self.dataSetCallback(m)

    def setWidgetValue(self, val):
        self.dsbm11.setValue(val.m11)
        self.dsbm12.setValue(val.m12)
        self.dsbm13.setValue(val.m13)
        self.dsbm14.setValue(val.m14)

        self.dsbm21.setValue(val.m21)
        self.dsbm22.setValue(val.m22)
        self.dsbm23.setValue(val.m23)
        self.dsbm24.setValue(val.m24)

        self.dsbm31.setValue(val.m31)
        self.dsbm32.setValue(val.m32)
        self.dsbm33.setValue(val.m33)
        self.dsbm34.setValue(val.m34)

        self.dsbm41.setValue(val.m41)
        self.dsbm42.setValue(val.m42)
        self.dsbm43.setValue(val.m43)
        self.dsbm44.setValue(val.m44)


def getInputWidget(dataType, dataSetter, defaultValue):
    '''
    factory method
    '''
    if dataType == DataTypes.Float:
        return FloatInputWidget(dataSetCallback=dataSetter, defaultValue=defaultValue)
    if dataType == DataTypes.Int:
        return IntInputWidget(dataSetCallback=dataSetter, defaultValue=defaultValue)
    if dataType == DataTypes.String:
        return StringInputWidget(dataSetCallback=dataSetter, defaultValue=defaultValue)
    if dataType == DataTypes.Bool:
        return BoolInputWidget(dataSetCallback=dataSetter, defaultValue=defaultValue)
    if dataType == DataTypes.FloatVector3:
        return FloatVector3InputWidget(dataSetCallback=dataSetter, defaultValue=defaultValue)
    if dataType == DataTypes.FloatVector4:
        return FloatVector4InputWidget(dataSetCallback=dataSetter, defaultValue=defaultValue)
    if dataType == DataTypes.Quaternion:
        return QuatInputWidget(dataSetCallback=dataSetter, defaultValue=defaultValue)
    if dataType == DataTypes.Matrix33:
        return Matrix33InputWidget(dataSetCallback=dataSetter, defaultValue=defaultValue)
    if dataType == DataTypes.Matrix44:
        return Matrix44InputWidget(dataSetCallback=dataSetter, defaultValue=defaultValue)
    if dataType == DataTypes.Exec:
        return ExecInputWidget(dataSetCallback=dataSetter, defaultValue=None)
    return None
