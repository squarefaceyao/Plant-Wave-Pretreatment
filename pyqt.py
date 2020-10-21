from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
import plotly.graph_objs as go
import plotly.offline as plo
import pandas as pd
import numpy as np
import sys
import os
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class PlotlyQtDemo(QWidget):
    def __init__(self):
        super(PlotlyQtDemo, self).__init__()
        print(QDir.currentPath())
        self.initUi()

    def initUi(self):
        #界面最大化
        self.showMaximized()
        # self.resize(1200, 800)
        # 设置界面标题
        self.setWindowTitle('Plotly_Qt_Demo')
        # 界面主布局为水平布局
        self.mainLayout = QHBoxLayout(self)
        # self.mainLayout.setContentsMargins(0, 0, 0, 0)
        # 添加分离部件，分割窗口
        self.splitter = QSplitter(Qt.Horizontal)

        self.lefWidget = QWidget()
        self.leftLayout = QFormLayout(self.lefWidget)
        self.leftLayout.setVerticalSpacing(50)

        self.titleBox = QHBoxLayout()
        self.titleLabel = QLabel('植物电信号数据处理软件')
        self.titleLabel.setStyleSheet("QLabel{font-size:25px;font-weight:bold;}")
        self.titleBox.addWidget(self.titleLabel, alignment=Qt.AlignCenter)
        self.leftLayout.addRow(self.titleBox)

        self.hbox = QHBoxLayout()
        # 添加选择文件按钮
        self.choose_file_btn = QPushButton('选择文件')
        # 点击选择文件按钮之后 触发choose_file_btn_func方法，连接起来
        self.choose_file_btn.clicked.connect(self.choose_file_btn_func)
        self.choose_file_edit = QLineEdit()
        # 设置 文件路径的文本框只能读不能写
        self.choose_file_edit.setReadOnly(True)
        self.leftLayout.addRow(self.choose_file_btn, self.choose_file_edit)
        self.new_file_name_edit = QLineEdit()
        self.leftLayout.addRow('保存新文件的名字:', self.new_file_name_edit)
        self.hbox1 = QHBoxLayout()
        self.hbox1.setSpacing(10)
        int_validato = QIntValidator(self)
        # 4个单行文本编辑控件
        self.sequence_edit_1 = QLineEdit()
        self.sequence_edit_2 = QLineEdit()
        self.sequence_edit_3 = QLineEdit()
        self.sequence_edit_4 = QLineEdit()
        # 设置只能输入数字
        self.sequence_edit_1.setValidator(int_validato)
        self.sequence_edit_2.setValidator(int_validato)
        self.sequence_edit_3.setValidator(int_validato)
        self.sequence_edit_4.setValidator(int_validato)
        # 在布局中添加 这4个控件
        self.hbox1.addWidget(self.sequence_edit_1)
        self.hbox1.addWidget(self.sequence_edit_2)
        self.hbox1.addWidget(self.sequence_edit_3)
        self.hbox1.addWidget(self.sequence_edit_4)
        self.leftLayout.addRow('请输入读取序列的标号(4个):', self.hbox1)

        self.readDataBox = QHBoxLayout()
        # 添加读取数据的按钮
        self.readDataBtn = QPushButton('读取数据')
        # 将读取数据按钮 点击之后运行绑定的函数，绑定到 readDataBtn_func
        self.readDataBtn.clicked.connect(self.readDataBtn_func)
        self.readDataBtn.setMinimumSize(120, 30)
        # 将读取数据按钮添加到布局中
        self.readDataBox.addWidget(self.readDataBtn, alignment=Qt.AlignCenter)

        self.leftLayout.addRow(self.readDataBox)
        # 2个单行文本编辑控件a波起始点，b波起始点
        self.a_wave_starting_point = QLineEdit()
        self.b_wave_starting_point = QLineEdit()
        self.leftLayout.addRow('请输入a波起始点:', self.a_wave_starting_point)
        self.leftLayout.addRow('请输入b波起始点:', self.b_wave_starting_point)

        self.hbox2 = QHBoxLayout()
        # 添加波形拼接并去除基线的按钮
        self.waveform_splicing_btn = QPushButton('波形拼接并去除基线')
        # 将波形拼接并去除基线的按钮 点击之后运行绑定的函数，绑定到 waveform_splicing_btn_func
        self.waveform_splicing_btn.clicked.connect(self.waveform_splicing_btn_func)
        self.waveform_splicing_btn.setMinimumSize(120, 30)

        self.hbox2.addWidget(self.waveform_splicing_btn, alignment=Qt.AlignCenter)
        self.leftLayout.addRow(self.hbox2)

        # 添加QWebEngineView浏览器模块窗口
        self.browser = QWebEngineView()
        self.splitter.addWidget(self.lefWidget)
        self.splitter.addWidget(self.browser)
        self.splitter.setSizes([100, 800])

        self.mainLayout.addWidget(self.splitter)

    def choose_file_btn_func(self):
        # QFileDialog.getOpenFileName选择 文件对话框
        fileName, filetype = QFileDialog.getOpenFileName(self,
                                                                "选取文件",
                                                                os.getcwd(),  # 起始路径
                                                                "All Files (*);;CSV Files (*.csv)")  # 设置文件扩展名过滤,用双分号间隔

        if fileName == "":
            pass
        else:
            self.choose_file_edit.setText(fileName)

    def waveform_splicing_btn_func(self):
        aData = int(self.a_wave_starting_point.text())
        bData = int(self.b_wave_starting_point.text())
        self.chart_a, self.chart_b = self.plant.cheak_ab(a=aData, b=bData)
        ss = self.plant.merge_ab(a=aData, b=bData)
        basline = self.plant.baseline(ss)
        self.plant.save_ab(self.new_file_name_edit.text(), basline)

        self.chartWidget = QWidget()
        self.chartLayout = QVBoxLayout(self.chartWidget)
        self.chartCanvas = MyFigureCanvas()
        self.chartNavigationToolbar = NavigationToolbar2QT(self.chartCanvas, self.chartWidget)
        self.chartLayout.addWidget(self.chartNavigationToolbar)
        self.chartLayout.addWidget(self.chartCanvas)

        ax1 = self.chartCanvas.figure.add_subplot(211)
        self.chart_a.plot(ax=ax1)

        ax2 = self.chartCanvas.figure.add_subplot(212)
        self.chart_b.plot(ax=ax2)

        self.chartWidget.show()



    def readDataBtn_func(self):
        print(self.choose_file_edit.text())
        print(self.new_file_name_edit.text())
        print(self.sequence_edit_1.text())
        print(self.sequence_edit_2.text())
        print(self.sequence_edit_3.text())
        print(self.sequence_edit_4.text())

        self.fileName = self.choose_file_edit.text()

        self.plant = Plant(self.fileName, self.sequence_edit_1.text(), self.sequence_edit_2.text(),
                      self.sequence_edit_3.text(), self.sequence_edit_4.text())
        self.plant.plot()
        print(sys.path[0] + '/demo.html')
        # self.browser.setUrl(QUrl(sys.path[0] + '/demo.html'))
        self.browser.setUrl(QUrl('file:///'+sys.path[0] + '/demo.html'))






class Plant(object):
    def __init__(self, filename, q, w, e, r):
        self.filename = filename
        self.q = q
        self.w = w
        self.e = e
        self.r = r
        print("当前打开的文件{},读取{}、{}、{}、{}列信号".format(filename, q, w, e, r))

    def read_cl(self):
        df = pd.read_csv(self.filename)
        signal = df[[self.q, self.w, self.e, self.r]]
        return signal

    def merge_ab(self, a, b):
        self.a = a
        self.b = b
        signal = self.read_cl()
        al = list()
        al = signal[a:a + 588]
        ss = al.append(signal[b:b + 588]).reset_index(drop=True)
        print(ss.shape)
        return ss

    def save_ab(self, savename, df):
        pd.DataFrame(df).to_csv(savename, index=False, header=False)
        print("成功保存到文件夹{}".format(savename))

    def cheak_ab(self, a, b):
        """再次观察裁剪的ab波"""
        signal = self.read_cl()

        chart_a = signal[a:a + 588]
        chart_b = signal[b:b + 588]
        return chart_a, chart_b

    def plot(self):
        ss = self.read_cl()
        x = np.arange(len(ss['{}'.format(self.q)]))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=ss['{}'.format(self.q)], name='{}'.format(self.q), line_shape='spline'))
        fig.add_trace(go.Scatter(x=x, y=ss['{}'.format(self.w)], name='{}'.format(self.w), line_shape='spline'))
        fig.add_trace(go.Scatter(x=x, y=ss['{}'.format(self.e)], name='{}'.format(self.e), line_shape='spline'))
        fig.add_trace(go.Scatter(x=x, y=ss['{}'.format(self.r)], name='{}'.format(self.r), line_shape='spline'))
        fig.update_layout(legend=dict(y=0.5, traceorder='reversed', font_size=16))

        # fig.show()
        plo.plot(fig, filename='demo.html', auto_open=False)



    def baseline(self, df):
        """merge的时候就把基线去掉
            lambda 表达式用上
            需要df遍历
            每一个df里面的数值，减去第一个df的值
            传进来的df是竖着的

        """
        df = df.T
        df1 = pd.DataFrame()
        col = list(df.columns)
        print("正在去除基线，请稍等。。。")
        for i in range(len(df.columns)):
            df1[col[i]] = df.apply(lambda a: a[i] - a[0], axis=1)
        return df1.T

class MyFigureCanvas(FigureCanvas):
    """
    画布
    """
    def __init__(self):
        # 画布上初始化一个图像
        width = 14
        height = 12
        dpi = 100
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.figure)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    Window = PlotlyQtDemo()
    Window.show()
    sys.exit(app.exec_())