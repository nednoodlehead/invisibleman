from PyQt5.QtWidgets import QWidget, QLabel, QTextEdit, QPushButton, QComboBox, QLineEdit, QFrame, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QFont
from gui.insert_functions import refresh_asset_categories, refresh_asset_location, refresh_asset_types, fetch_categories_and_years, replace_json_target
from volatile.write_to_volatile import add_to_asset_list, add_to_type_or_location

class GenericAddJsonWindow(QWidget):
     def __init__(self, target: str, parent_window):
          super().__init__()
          self.target = target  # deciding what json file to write to
          self.parent_window = parent_window  # used to tell parent to update the comboboxes when done
          # value should be either: "Category", "Type", "Location"
          # should each of these have their own file? or one file?



          font = QFont()
          font.setPointSize(10)
          self.setFont(font)
          self.json_write_to_button = QPushButton("Update", self)
          self.json_write_to_button.setObjectName(u"json_write_to_button")
          self.json_write_to_button.setGeometry(QRect(10, 410, 75, 23))
          self.json_exit_button = QPushButton("Exit", self)
          self.json_exit_button.setObjectName(u"json_exit_button")
          self.json_exit_button.setGeometry(QRect(370, 410, 75, 23))
          self.json_new_value_text = QLineEdit(self)
          self.json_new_value_text.setObjectName(u"json_new_value_text")
          self.json_new_value_text.setGeometry(QRect(130, 270, 113, 20))
          self.json_new_value_label = QLabel("Add new value", self)
          self.json_new_value_label.setObjectName(u"json_new_value_label")
          self.json_new_value_label.setGeometry(QRect(80, 270, 51, 16))
          self.json_conditional_years_text = QLineEdit(self)
          self.json_conditional_years_text.setObjectName(u"json_conditional_years_text")
          self.json_conditional_years_text.setGeometry(QRect(130, 310, 113, 20))
          self.json_conditional_years_label = QLabel("Years until expiry", self)
          self.json_conditional_years_label.setObjectName(u"json_conditional_years_label")
          self.json_conditional_years_label.setGeometry(QRect(20, 310, 111, 21))
          self.json_value_frame = QFrame(self)
          self.json_value_frame.setObjectName(u"json_value_frame")
          self.json_value_frame.setGeometry(QRect(90, 40, 201, 211))
          self.json_value_frame.setFrameShape(QFrame.StyledPanel)
          self.json_value_frame.setFrameShadow(QFrame.Raised)
          self.verticalLayoutWidget = QWidget(self.json_value_frame)
          self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
          self.verticalLayoutWidget.setGeometry(QRect(-1, 0, 211, 211))
          self.json_value_layout = QVBoxLayout(self.verticalLayoutWidget)
          self.json_value_layout.setObjectName(u"json_value_layout")
          self.json_value_layout.setContentsMargins(0, 0, 0, 0)
          self.json_years_frame = QFrame(self)
          self.json_years_frame.setObjectName(u"json_years_frame")
          self.json_years_frame.setGeometry(QRect(290, 40, 41, 211))
          self.json_years_frame.setFrameShape(QFrame.StyledPanel)
          self.json_years_frame.setFrameShadow(QFrame.Raised)
          self.verticalLayoutWidget_2 = QWidget(self.json_years_frame)
          self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
          self.verticalLayoutWidget_2.setGeometry(QRect(0, 0, 41, 211))
          self.json_years_layout = QVBoxLayout(self.verticalLayoutWidget_2)
          self.json_years_layout.setObjectName(u"json_years_layout")
          self.json_years_layout.setContentsMargins(0, 0, 0, 0)
          self.json_button_frame = QFrame(self)
          self.json_button_frame.setObjectName(u"json_button_frame")
          self.json_button_frame.setGeometry(QRect(50, 40, 41, 211))
          self.json_button_frame.setFrameShape(QFrame.StyledPanel)
          self.json_button_frame.setFrameShadow(QFrame.Raised)
          self.verticalLayoutWidget_3 = QWidget(self.json_button_frame)
          self.verticalLayoutWidget_3.setObjectName(u"verticalLayoutWidget_3")
          self.verticalLayoutWidget_3.setGeometry(QRect(0, 0, 41, 211))
          self.json_button_layout = QVBoxLayout(self.verticalLayoutWidget_3)
          self.json_button_layout.setObjectName(u"json_button_layout")
          self.json_button_layout.setContentsMargins(0, 0, 0, 0)
          self.json_values_label = QLabel("Values", self)
          self.json_values_label.setObjectName(u"json_values_label")
          self.json_values_label.setGeometry(QRect(160, 20, 51, 16))
          self.json_years_label = QLabel("Years", self)  # also conditional...
          self.json_years_label.setObjectName(u"json_years_label")
          self.json_years_label.setGeometry(QRect(290, 20, 61, 16))
          self.json_add_new_value_button = QPushButton("Add new value", self)
          self.json_add_new_value_button.setObjectName(u"json_add_new_value_button")
          self.json_add_new_value_button.setGeometry(QRect(250, 270, 91, 23))
          font1 = QFont()
          font1.setPointSize(8)
          self.json_add_new_value_button.setFont(font1)
          self.json_add_new_value_button.setFont(font1)        
          if self.target != "Category":
                self.json_conditional_years_label.hide()
                self.json_conditional_years_text.hide()
                self.json_years_frame.setStyleSheet("")
                self.json_years_label.hide()
          self.fill_layout_with_content()
          self.json_value_frame.raise_()
          self.json_add_new_value_button.clicked.connect(self.add_new_value_from_user)
          self.json_write_to_button.clicked.connect(self.write_changes)
                

     def get_values_and_process(self):
          years = self.json_conditional_text.text()
          data = self.json_value_text.text()
          if years.isdigit():
               new_int = int(years)
               add_to_asset_list(data, new_int)
          else:
               add_to_type_or_location(data, self.target)
          self.close()
          # also need to send signal to main program to tell it to refresh the relevant combobox

     def fill_layout_with_content(self):
          print(f"self.cate: {self.target} {self.target == "Category"}")
          data = None
          if self.target == "Category":
               data = fetch_categories_and_years(self)
               for cate, years in data.items():
                    self.json_value_layout.addWidget(QLineEdit(cate))
                    self.json_years_layout.addWidget(QLineEdit(str(years)))
                    button = self.make_x_button()
                    self.json_button_layout.addWidget(button)
                    
          else:
               if self.target == "Type":
                    data = refresh_asset_types(self)
               else:
                    data = refresh_asset_location(self)
               for item in data:
                    self.json_value_layout.addWidget(QLineEdit(item))
                    button = self.make_x_button()
                    self.json_button_layout.addWidget(button)
                    
     def make_x_button(self):
          button = QPushButton("X")
          button.clicked.connect(lambda: self.button_remove_item(button))
          return button
     
     def button_remove_item(self,button):
          index = self.json_button_layout.indexOf(button)
          self.remove_wid(index)

     def remove_wid(self, index):
          parts = [self.json_value_layout, self.json_button_layout]
          if self.target == "Category":  # if the additional rows exist, also affect that part :D
               parts.append(self.json_years_layout)
          for layout in parts:
               item = layout.itemAt(index)
               wid = item.widget()
               wid.setParent(None)

     def add_new_value_from_user(self):
          if not self.json_new_value_text.text() == "":
               current_index = len(self.json_button_layout) + 1
               if self.target == "Category":
                    self.json_years_layout.addWidget(QLineEdit(self.json_conditional_years_text.text()))
               self.json_value_layout.addWidget(QLineEdit(self.json_new_value_text.text()))
               button = self.make_x_button()
               self.json_button_layout.addWidget(button)
          else:
               # maybe make prompt to tell user to be smart
               print("please enter value")
          
     def write_changes(self):
          data = []
          length = range(self.json_value_layout.count())
          if self.target == "Category":
               data = {}
               for index in length:
                    key = self.json_value_layout.itemAt(index).widget().text()
                    val = self.json_years_layout.itemAt(index).widget().text()
                    data[key] = val
          else:
               for index in length:
                    val = self.json_value_layout.itemAt(index).widget().text()
                    data.append(val)
          replace_json_target(self.target, data)
          self.parent_window.refresh_combobox(self.target)
          self.close()                   
          # write changes to json file
          # probably just pull from the layouts and create a dict, then write it?
