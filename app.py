"""
Copyright © 2020 Stephen McEntee
Licensed under the MIT license. 
See LICENSE file for details https://github.com/qwilka/metadata-manager-2015/blob/master/LICENSE
"""
import os
import sys
module_path = os.path.dirname(os.getcwd()) 
if module_path not in sys.path:
    sys.path.append(module_path)  

from PyQt5.QtWidgets import QApplication

from utilities.vnlogger import setup_logger
logger = setup_logger(logfile="visinum_messages.log", lvl='INFO',
                                   redir_STOUT=False)

from mainwindow import MainWindow

VERSION = '0.0'

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Visinum-Metadata")
    app.setOrganizationName("Qwilka")
    app.setOrganizationDomain("qwilka.github.io")
    app.setStyle("fusion")  
    mainwindow = MainWindow()
    ##app.mainwindow = mainwindow
    mainwindow.show()
    sys.exit(app.exec_())   # app.exec_()


if __name__ == "__main__":
    main()
