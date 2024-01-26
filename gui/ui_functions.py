from gui.auto import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QPushButton, QMessageBox, QMenu, QTableWidget, QCheckBox
from PyQt5.QtCore import QDate, Qt, QDate
from PyQt5.QtGui import QCursor
from util.data_types import InventoryObject, TableObject, create_inventory_object
from db.fetch import fetch_all, fetch_all_for_table, fetch_from_uuid_to_update
from db.insert import new_entry
from db.update import update_full_obj
from gui.notes_window import NotesWindow
from volatile.write_to_volatile import write_to_config, read_from_config
from types import MethodType
from gui.insert_functions import update_replacement_date, refresh_asset_types, add_asset_type, refresh_asset_categories, fetch_all_asset_types, refresh_asset_location
from gui.add_item_window import GenericAddJsonWindow
from datetime import datetime

class MainProgram(QMainWindow, Ui_MainWindow):
     def __init__(self, parent=None):
          super().__init__(parent)
          self.setupUi(self)
          self.imported_methods()  # call the imported methods into scope of the class
          self.active_notes_window = None
          self.active_json_window = None
          # there is some argument to use a QTableView instead of a QTableWidget, since the view better supports
          # M/V style programming, which would (in theory) significantly improve the performance of certain
          # operations, namely filtering. would require quite a lot of refactoring though. so maybe another time :)
          # https://stackoverflow.com/questions/6785481/how-to-implement-a-filter-option-in-qtablewidget
          # the concept is that QTableWidget has a built-in model, and a QTableView does not, so you can edit it
          
          # ui functions
          self.ham_menu_button.clicked.connect(self.toggle_burger)
          self.populate_table_with(fetch_all_for_table())  # TODO do this more! (when make / update data)
          self.ham_button_insert.clicked.connect(lambda: self.swap_to_window(1))
          self.ham_button_view.clicked.connect(lambda: self.swap_to_window(0))
          self.ham_button_analytics.clicked.connect(lambda: self.swap_to_window(2))
          self.ham_button_reports.clicked.connect(lambda: self.swap_to_window(3))
          self.insert_asset_category_combobox.currentIndexChanged.connect(self.update_replacement_date)
          self.insert_insert_button.clicked.connect(self.check_data_and_insert)
          self.insert_clear_selections_button.clicked.connect(self.set_insert_data_to_default)
          self.refresh_table_button.clicked.connect(lambda: self.populate_table_with(fetch_all_for_table()))
          self.main_table.setSortingEnabled(True)
          self.sort_by_button.clicked.connect(lambda: self.filter_all_columns("Hard"))
          self.view_columns_button.clicked.connect(self.view_button_reveal_checkboxes)
          # make all the checboxes checked by default and make the checkboxes do something when clicked
          # probably worth adding json support at some point, so when app is closed, it is written to json, and loaded on start
          # but that also requires setting the exit function. TODO later :>
          self.config = read_from_config()
          self.default_columns = ["Name", "Serial Number", "Manufacturer", "Price", "Asset Category", "Asset Type", "Assigned To", "Asset Location",
                                 "Purchase Date", "Install Date", "Replacement Date", "Notes"]
          for count, checkbox in enumerate((self.checkbox_name, self.checkbox_serial, self.checkbox_manufacturer, self.checkbox_price,
          self.checkbox_assetcategory, self.checkbox_assettype, self.checkbox_assignedto, self.checkbox_assetlocation, self.checkbox_purchasedate,
          self.checkbox_installdate, self.checkbox_replacementdate, self.checkbox_notes)):
               self.handle_checkboxes_and_columns(count, checkbox)
          # populating combo boxes. "" is an empty default value 
          cat, typ, loc = self.fetch_all_asset_types()
          self.insert_asset_category_combobox.addItem("")
          self.insert_asset_type_combobox.addItem("")
          self.insert_asset_location_combobox.addItem("")
          self.insert_asset_category_combobox.addItems(cat)
          self.insert_asset_type_combobox.addItems(typ)
          self.insert_asset_location_combobox.addItems(loc)
          self.insert_status_bool.addItems(["Enabled", "Disabled"])
          # thr possible? might be quicker to load "non-visible by defualt" content on sep thread
          self.insert_install_date_fmt.setDate(QDate.currentDate())
          self.insert_purchase_date_fmt.setDate(QDate.currentDate())
          self.insert_price_spinbox.setMaximum(99999.99)
          # leave the insert_replacement_date_fmt for when the user selects the hardware type
          self.insert_asset_category_add_option.clicked.connect(lambda: self.display_generic_json("Category"))
          self.insert_asset_type_add_option.clicked.connect(lambda: self.display_generic_json("Type"))
          self.insert_asset_location_add_option.clicked.connect(lambda: self.display_generic_json("Location"))
          # edit buttons
          self.set_table_size_and_headers(self.default_columns)
          self.main_table.setContextMenuPolicy(Qt.CustomContextMenu)
          self.main_table.customContextMenuRequested.connect(self.display_table_context_menu)
          
     # overwritten methods
     
     def closeEvent(self, event):
          self.write_config()
          event.accept()
          

     # regular methods
     def imported_methods(self):
          # for loop at some point? lmao
          self.update_replacement_date = MethodType(update_replacement_date, self)
          self.refresh_asset_types = MethodType(refresh_asset_types, self)
          self.refresh_asset_category = MethodType(refresh_asset_categories, self)
          self.refresh_asset_location = MethodType(refresh_asset_location, self)
          self.fetch_all_asset_types = MethodType(fetch_all_asset_types, self)

     def display_error_message(self, error: str):
          msg = QMessageBox()
          msg.setText(error)
          msg.setWindowTitle("Error")
          msg.exec_()

     def display_table_context_menu(self, position=None):
          menu = QMenu()
          menu.addAction("Update", lambda: self.send_update_data_to_insert(self.main_table.itemAt(position).row()))
          menu.exec_(QCursor.pos())

     def view_button_reveal_checkboxes(self):
          if self.view_toggle_frame.width() == 690:
               self.view_toggle_frame.setFixedWidth(80)
          else:
               self.view_toggle_frame.setFixedWidth(690)

     def handle_checkboxes_and_columns(self, column: int, box: QCheckBox):
          # box.clicked.connect(lambda: self.main_table.setColumnHidden(column, not box.isChecked))
          
          def button_target():
               self.main_table.setColumnHidden(column, not box.isChecked())
          # if you replace this function and col with lambda, it does not work. on god
          box.clicked.connect(button_target)
          if self.config["checkboxes"][self.default_columns[column]] is True:
               box.setChecked(True)               
          else:
               self.main_table.setColumnHidden(column, True)
               pass  # set setchecked false by default on startup?

     def tester(self):
          print("here")

          
     def send_update_data_to_insert(self, index):
          uuid = self.main_table.item(index, self.main_table.columnCount() -1).text()
          obj = fetch_from_uuid_to_update(uuid)
          self.swap_to_window(1)
          self.update_insert_page_from_obj(obj)

     def update_insert_page_from_obj(self, inventory_obj: InventoryObject):
          self.insert_name_text.setText(inventory_obj.name)
          self.insert_serial_text.setText(inventory_obj.serial)
          self.insert_manufacturer_text.setText(inventory_obj.manufacturer)
          self.insert_price_spinbox.setValue(float(inventory_obj.price))
          cat_index = self.insert_asset_category_combobox.findText(inventory_obj.assetcategory)
          self.insert_asset_category_combobox.setCurrentIndex(cat_index)
          type_index = self.insert_asset_type_combobox.findText(inventory_obj.assettype)
          self.insert_asset_type_combobox.setCurrentIndex(type_index)
          loc_index = self.insert_asset_location_combobox.findText(inventory_obj.assetlocation)
          self.insert_asset_location_combobox.setCurrentIndex(loc_index)
          self.insert_assigned_to_text.setText(inventory_obj.assignedto)
          self.insert_purchase_date_fmt.setDate(datetime.fromisoformat(inventory_obj.purchasedate))
          self.insert_install_date_fmt.setDate(datetime.fromisoformat(inventory_obj.installdate))
          self.insert_replacement_date_fmt.setDate(datetime.fromisoformat(inventory_obj.replacementdate))
          self.insert_notes_text.setText(inventory_obj.notes)
          if self.insert_status_bool == 0:
               self.insert_status_bool.setCurrentIndex(1)
          else:
               self.insert_status_bool.setCurrentIndex(0)
          self.insert_uuid_text.setText(inventory_obj.uniqueid)
          
                              
     def toggle_burger(self):
          if self.ham_menu_frame.height() == 250:
               self.ham_menu_frame.setFixedHeight(50)
               
          else:
               self.ham_menu_frame.setFixedHeight(250)

     def swap_to_window(self, index: int):
          self.stackedWidget.setCurrentIndex(index)
          # grey out button that is selected by index?

     def write_config(self):
          to_write = {
               "Name": self.checkbox_name.isChecked(),
               "Serial Number": self.checkbox_serial.isChecked(),
               "Manufacturer": self.checkbox_manufacturer.isChecked(),
               "Price": self.checkbox_price.isChecked(),
               "Asset Category": self.checkbox_assetcategory.isChecked(),
               "Asset Type": self.checkbox_assettype.isChecked(),
               "Assigned To": self.checkbox_assignedto.isChecked(),
               "Asset Location": self.checkbox_assetlocation.isChecked(),
               "Purchase Date": self.checkbox_purchasedate.isChecked(),
               "Install Date": self.checkbox_installdate.isChecked(),
               "Replacement Date": self.checkbox_replacementdate.isChecked(),
               "Notes": self.checkbox_notes.isChecked()
          }
          print("to write:", to_write)
          checked = True if self.ham_menu_frame.height() == 250 else False
          write_to_config(checked, to_write)
     

     def populate_table_with(self, data: [TableObject]):
          self.main_table.setRowCount(len(data))
          self.main_table.setColumnCount(len(data[0]))  # set the column count to the size of the first data piece
          for row, rowdata in enumerate(data):
               for col, value in enumerate(rowdata):
                    item = QTableWidgetItem(str(value))
                    if col == 11:
                         if value == '':
                              button = self.generate_notes_button(data[row].uniqueid, "Add Notes")                              
                              self.main_table.setCellWidget(row, col, button)
                         else:
                              button = self.generate_notes_button(data[row].uniqueid, "View Notes")
                              self.main_table.setCellWidget(row, col, button)
                    else:
                         self.main_table.setItem(row, col, item)

     def generate_notes_button(self, uuid: str, display: str):  # uuid so we can update to the right column
          button = QPushButton()
          button.setText(display)
          button.clicked.connect(lambda: self.display_notes(uuid))
          return button
          

     def display_notes(self, uuid: str):
          # will be a text box 
          self.active_notes_window = NotesWindow(uuid)
          self.active_notes_window.show()
          position = self.pos()
          position.setX(position.x() + 250)
          position.setY(position.y() + 250)
          self.active_notes_window.move(position)      

     
     def filter_columns(self, *args):
          for selected_column in args:
              pass 

     def display_generic_json(self, target: str):
          self.active_json_window = GenericAddJsonWindow(target, self)
          self.active_json_window.show()
          position = self.pos()
          position.setX(position.x() + 250)
          position.setY(position.y() + 250)
          self.active_json_window.move(position)

     def refresh_combobox(self, target: str):
          if target == "Category":
               self.insert_asset_category_combobox.clear()
               self.insert_asset_category_combobox.addItem("")
               self.insert_asset_category_combobox.addItems(self.refresh_asset_category())
          elif target == "Type":
               self.insert_asset_type_combobox.clear()
               self.insert_asset_type_combobox.addItem("")
               self.insert_asset_type_combobox.addItems(self.refresh_asset_types())
          else:
               self.insert_asset_location_combobox.clear()
               self.insert_asset_location_combobox.addItem("")
               self.insert_asset_location_combobox.addItems(self.refresh_asset_location())

     def check_data_and_insert(self):
          required = {"Serial": self.insert_serial_text, "Manufacturer": self.insert_manufacturer_text, "Asset Category":self.insert_asset_category_combobox,
          "Asset Type": self.insert_asset_type_combobox, "Asset Location": self.insert_asset_location_combobox}
          missing = []
          for name, item in required.items():
               try:
                    if item.text() == "":
                         missing.append(name)
               except AttributeError:  # comboboxes !!
                    if item.currentText() == "":
                         missing.append(name)
          if len(missing) != 0:
               self.display_error_message(f"Missing fields: {missing}")
          else:
               # we are creating a new entry if this is an empty value 
               if self.insert_uuid_text.text() == '':
                    
                    obj = create_inventory_object(self.insert_name_text.text(), self.insert_serial_text.text(), self.insert_manufacturer_text.text(),
                                            self.insert_price_spinbox.text(), self.insert_asset_category_combobox.currentText(), self.insert_asset_type_combobox.currentText(),
                                            self.insert_assigned_to_text.text(), self.insert_asset_location_combobox.currentText(), self.insert_purchase_date_fmt.text(), 
                                            self.insert_install_date_fmt.text(), self.insert_replacement_date_fmt.text(), self.insert_notes_text.toPlainText(),
                                            self.insert_status_bool.currentText())
                    new_entry(obj)               
               else:
                    # we are updating an existing entry! (since the uuid string was set)
                    obj = InventoryObject(self.insert_name_text.text(), self.insert_serial_text.text(), self.insert_manufacturer_text.text(), self.insert_price_spinbox.text(),
                                          self.insert_asset_category_combobox.currentText(), self.insert_asset_type_combobox.currentText(), self.insert_assigned_to_text.text(), self.insert_asset_location_combobox.currentText(),
                                          self.insert_purchase_date_fmt.text(), self.insert_install_date_fmt.text(), self.insert_replacement_date_fmt.text(),
                                          self.insert_notes_text.toPlainText(), self.insert_status_bool.currentText(), self.insert_uuid_text.text())
                    update_full_obj(obj)
               self.set_insert_data_to_default()
               self.populate_table_with(fetch_all_for_table())  # this will overwrite any filters / views

     def set_insert_data_to_default(self):
          today = QDate.currentDate()
          self.insert_name_text.setText("")
          self.insert_serial_text.setText("")
          self.insert_manufacturer_text.setText("")
          self.insert_price_spinbox.setValue(0.00)
          self.insert_asset_category_combobox.setCurrentIndex(0)  # to the empty string!
          self.insert_asset_type_combobox.setCurrentIndex(0)
          self.insert_asset_location_combobox.setCurrentIndex(0)
          self.insert_assigned_to_text.setText("")
          self.insert_purchase_date_fmt.setDate(today)
          self.insert_install_date_fmt.setDate(today)
          self.insert_replacement_date_fmt.setDate(today)
          self.insert_notes_text.setText("")
          self.insert_status_bool.setCurrentIndex(0)
          self.insert_uuid_text.setText("")

     def set_table_size_and_headers(self, headers: [str]):
          # kept sort of abigious since headers can be changed. if it was always all the headers it could be hardcoded
          headers.append("UUID")
          length = len(headers)
          self.main_table.setColumnCount(length)
          self.main_table.setHorizontalHeaderLabels(headers)
          # set the sizes of certain columns as needed
          for count, column_title in enumerate(headers):
               if column_title == "Asset Category":
                    header = self.main_table.columnWidth(count)
                    # maybe value should be calculated based off the longest string from the relevant json
                    self.main_table.setColumnWidth(count, 150)
               elif column_title == "Replacement Date":
                    self.main_table.setColumnWidth(count, 120)
          # alternating row colors :D
          self.main_table.setAlternatingRowColors(True)
          self.main_table.setColumnHidden(length -1, True)  # must be done here
               
     def filter_all_columns(self, word: str):
          for row_num in range(self.main_table.rowCount()):
               match = False
               for col_num in range(self.main_table.columnCount()):
                    cell = self.main_table.item(row_num, col_num)
                    if cell is None:
                         continue
                    else:
                         cell_content = cell.text()
                         if word in cell_content:
                              match = True
                              break
               if match is False:
                    self.main_table.setRowHidden(row_num, True)

     def clear_filter(self):
          pass
                              
          
               
