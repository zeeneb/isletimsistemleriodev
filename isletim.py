import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QAction, QMessageBox,
    QInputDialog, QFileDialog, QPushButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QTextCharFormat, QColor, QTextCursor


class EditorLogic:
    def __init__(self):
        print("Temel Metin Düzenleyici başlatıldı")

    def read_file(self, path: str) -> str:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Dosya bulunamadı: {path}")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            raise IOError(f"Dosya okunurken bir hata oluştu: {e}")

    def write_file(self, path: str, content: str):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            raise IOError(f"Dosya yazılırken bir hata oluştu: {e}")


class TextEditorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Temel Metin Düzenleyici")
        self.setGeometry(100, 100, 800, 600)

        self.logic = EditorLogic()
        self.current_file = None

        self.mainTextEdit = QTextEdit(self)
        self.setCentralWidget(self.mainTextEdit)
        self.mainTextEdit.setPlaceholderText("Metin giriniz...")

        self.statusBar().showMessage("Hazır")

        self.create_actions()
        self.create_menus()

    def create_actions(self):
        self.new_action = QAction("&Yeni", self)
        self.new_action.triggered.connect(self.file_new)
        self.new_action.setShortcut(QKeySequence.New)

        self.open_action = QAction("&Aç", self)
        self.open_action.triggered.connect(self.file_open)
        self.open_action.setShortcut(QKeySequence.Open)

        self.save_action = QAction("&Kaydet", self)
        self.save_action.triggered.connect(self.file_save)
        self.save_action.setShortcut(QKeySequence.Save)

        self.saveas_action = QAction("Farklı &Kaydet", self)
        self.saveas_action.triggered.connect(self.file_saveas)

        self.exit_action = QAction("&Çıkış", self)
        self.exit_action.triggered.connect(self.close)
        self.exit_action.setShortcut(QKeySequence.Quit)

        self.find_action = QAction("&Bul/Değiştir", self)
        self.find_action.triggered.connect(self.edit_find)

        self.replace_action = QAction("Değiştir (Kaldırıldı)", self) 

        self.about_action = QAction("Hakkında", self)
        self.about_action.triggered.connect(self.show_about)

    def create_menus(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&Dosya")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.saveas_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        edit_menu = menu_bar.addMenu("&Düzenle")
 
        edit_menu.addAction(self.find_action) 
        
        about_menu = menu_bar.addMenu("&Hakkında")
        about_menu.addAction(self.about_action)

    def file_new(self):
        self.mainTextEdit.clear()
        self.current_file = None
        self.setWindowTitle("Yeni Dosya | Metin Düzenleyici")
        self.statusBar().showMessage("Yeni dosya oluşturuldu")

    def file_open(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Dosya Aç", "", "Metin Dosyaları (*.txt);;Tüm Dosyalar (*.*)"
        )
        if filename:
            try:
                content = self.logic.read_file(filename)
                self.mainTextEdit.setText(content)
                self.current_file = filename
                self.setWindowTitle(f"{os.path.basename(filename)} - Metin Düzenleyici")
                self.statusBar().showMessage("Dosya yüklendi")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya açılırken hata: {e}")

    def file_save(self):
        if self.current_file:
            try:
                content = self.mainTextEdit.toPlainText()
                self.logic.write_file(self.current_file, content)
                self.statusBar().showMessage("Dosya kaydedildi")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Kaydedilirken hata: {e}")
        else:
            self.file_saveas()

    def file_saveas(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Farklı Kaydet", "", "Metin Dosyaları (*.txt);;Tüm Dosyalar (*.*)"
        )
        if filename:
            self.current_file = filename
            self.file_save()

    def edit_find(self):
        text, ok = QInputDialog.getText(self, "Bul", "Aranacak metin:")
        
        if ok and text:
            document = self.mainTextEdit.document()
            self.clear_formatting()

            format = QTextCharFormat()
            format.setBackground(QColor("yellow"))

            found_count = 0
            
            cursor = document.find(text)
            
            while not cursor.isNull():
                
                cursor.mergeCharFormat(format)
                found_count += 1
                
                cursor = document.find(text, cursor) 

            if found_count > 0:
                self.statusBar().showMessage(f"'{text}' metni {found_count} kez bulundu ve işaretlendi.")
                
                # Sadece Bul işleminden sonra değiştirme teklifi sunulur
                message_box = QMessageBox(self)
                message_box.setWindowTitle('Değiştirme Teklifi')
                message_box.setText(f"Bulunan '{text}' kelimesini değiştirmek ister misiniz?")
                
                btn_yes = message_box.addButton("Tamam", QMessageBox.YesRole)
                btn_no = message_box.addButton("Vazgeç", QMessageBox.NoRole)
                
                message_box.exec_()
                
                if message_box.clickedButton() == btn_yes:
                    self.edit_replace(text) # Değiştirme işlemini başlat
            else:
                self.statusBar().showMessage(f"'{text}' bulunamadı")

    def edit_replace(self, find_text):
        
        replace_text, ok2 = QInputDialog.getText(self, "Değiştir", f"'{find_text}' yerine geçecek yeni metin:")
        
        if ok2:
            content = self.mainTextEdit.toPlainText().replace(find_text, replace_text)
            self.mainTextEdit.setPlainText(content)
            self.clear_formatting() 
            self.statusBar().showMessage("Değiştirme işlemi tamamlandı")

    def clear_formatting(self):
        """Metindeki tüm karakter formatlarını (boyamaları) temizler."""
        
        temp_cursor = self.mainTextEdit.textCursor()
        temp_cursor.select(QTextCursor.Document)
        
        default_format = QTextCharFormat()
        default_format.setBackground(QColor(Qt.transparent))
        
        temp_cursor.mergeCharFormat(default_format)
        
        temp_cursor.movePosition(QTextCursor.Start)
        self.mainTextEdit.setTextCursor(temp_cursor)

    def show_about(self):
        QMessageBox.about(
            self,
            "Hakkında",
            "Temel Metin Düzenleyici\n\nHazırlayanlar:\n"
            "Zeynep Çeliknalça\nBeyzanur Tunçer\nMedine Eren\n"
            "Gönül Kazıcı\nSümeyye Onat\nDilara Karaoğlu\nAmine Zehra İlkay"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = TextEditorApp()
    editor.show()
    sys.exit(app.exec_())
