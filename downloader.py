import os
from PyQt5.QtCore import *
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager
from PyQt5.QtWidgets import QMessageBox

class Downloader(QNetworkAccessManager):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.finished.connect(self.on_download_finished)

    def download(self, url):
        # Make sure we are getting the actual file URL (not the domain)
        file_name = os.path.basename(QUrl(url).path())  # Get filename from the URL path
        if not file_name:  # If the URL doesn't end with a file name, use a default name
            file_name = "downloaded_file"
        
        download_path = os.path.join("downloads", file_name)  # Save to 'downloads' folder
        os.makedirs(os.path.dirname(download_path), exist_ok=True)  # Create folder if it doesn't exist

        request = QNetworkRequest(QUrl(url))
        reply = self.get(request)

        self.file = open(download_path, 'wb')  # Open file for writing in binary mode
        reply.downloadProgress.connect(self.on_download_progress)

    def on_download_finished(self, reply):
        if reply.error():
            QMessageBox.critical(None, "Download Error", f"Error: {reply.errorString()}")
        else:
            self.file.write(reply.readAll())  # Write the content to the file
            self.file.close()
            QMessageBox.information(None, "Download Complete", f"Downloaded to: {self.file.name}")

    def on_download_progress(self, bytes_received, total_bytes):
        # Optional: Can display progress (we're not using it right now)
        pass
