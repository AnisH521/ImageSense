from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView

import socket
import cv2
import os

class ImageClientApp(App):
    def build(self):
        layout = BoxLayout(orientation="horizontal")

        layout_left = BoxLayout(orientation="vertical")
        self.logo = Image(source="mustlogowhite.png", size_hint=(0.1, 0.1))
        layout_left.add_widget(self.logo)
        self.image = Image()
        layout_left.add_widget(self.image)

        layout_right = BoxLayout(orientation="vertical", size_hint=(0.6, 1))
        self.file_chooser = FileChooserListView(path=".")
        self.btn_capture = Button(text="Capture Image")
        self.btn_capture.bind(on_press=self.capture_image)
        layout_right.add_widget(self.file_chooser)
        layout_right.add_widget(self.btn_capture)

        layout.add_widget(layout_left)
        layout.add_widget(layout_right)

        return layout

    def capture_image(self, instance):

        selected_file = self.file_chooser.selection
        if not selected_file:
            return

        image_path = selected_file[0]

        captured_image = cv2.imread(image_path)

        img_bytes = cv2.imencode(".jpg", captured_image)[1].tobytes()

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("192.168.0.173", 2345))

        # Send the size of the image
        img_size = len(img_bytes).to_bytes(8, byteorder='big')
        client_socket.send(img_size)

        # Send the image data
        client_socket.send(img_bytes)

        # Receive the result image size
        result_size = client_socket.recv(8)
        result_size = int.from_bytes(result_size, byteorder='big')

        # Receive the result image data
        result_bytes = b""
        while len(result_bytes) < result_size:
            data = client_socket.recv(1024)
            if not data:
                break
            result_bytes += data

        base_dir = 'rst'
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        result_image_path = os.path.join(base_dir, 'result_image.jpg')
        with open(result_image_path, 'wb') as result_file:
            result_file.write(result_bytes)

        self.image.source = result_image_path
        self.image.reload()

if __name__ == "__main__":
    ImageClientApp().run()