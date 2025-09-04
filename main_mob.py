# Upgraded QR Code App with Hamburger Menu, Layout Improvements, and Themed Colors

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.dropdown import DropDown
from kivy.uix.togglebutton import ToggleButton
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.clock import Clock

import qrcode
from PIL import Image as PILImage
import io
import os
import webbrowser

# Color Scheme: Green, Purple, Blue, Royal Blue
Window.clearcolor = (0.08, 0.1, 0.2, 1)  # dark royal blue background

GREEN = (0.2, 0.8, 0.6, 1)
PURPLE = (0.6, 0.4, 0.8, 1)
BLUE = (0.3, 0.5, 0.9, 1)
ROYAL = (0.1, 0.3, 0.7, 1)

class SelectableLabel(RecycleDataViewBehavior, Label):
    index = None
    selected = False
    selectable = True

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            self.parent.select_with_touch(self.index, touch)
            return True
        return False

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        if is_selected:
            rv.parent.parent.parent.parent.load_history_item(index)


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    pass


class QRBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'

        # Side Menu
        self.menu = BoxLayout(orientation='vertical', size_hint=(0.15, 1), spacing=10, padding=10)
        self.add_widget(self.menu)

        self.link_btn = Button(text='LinkedIn', background_color=BLUE,
                               on_press=lambda x: webbrowser.open('https://linkedin.com/in/yourprofile'))
        self.gh_btn = Button(text='GitHub', background_color=PURPLE,
                             on_press=lambda x: webbrowser.open('https://github.com/yourprofile'))
        self.menu.add_widget(self.link_btn)
        self.menu.add_widget(self.gh_btn)

        # Main Area
        self.main = BoxLayout(orientation='vertical', size_hint=(0.85, 1), spacing=10, padding=20)
        self.add_widget(self.main)

        self.qr_history = []

        self.input = TextInput(hint_text='Enter text or URL', size_hint=(1, None), height=50, multiline=False,
                               background_color=(0.9, 1, 0.9, 1), foreground_color=(0, 0, 0, 1))
        self.main.add_widget(self.input)

        btn_row = BoxLayout(size_hint=(1, None), height=50, spacing=10)
        self.main.add_widget(btn_row)

        self.gen_btn = Button(text='Generate', background_color=GREEN)
        self.gen_btn.bind(on_press=self.generate_qr)
        btn_row.add_widget(self.gen_btn)

        self.save_btn = Button(text='Save', background_color=PURPLE)
        self.save_btn.bind(on_press=self.save_qr)
        btn_row.add_widget(self.save_btn)

        self.load_btn = Button(text='Load', background_color=BLUE)
        self.load_btn.bind(on_press=self.load_qr)
        btn_row.add_widget(self.load_btn)

        self.history_btn = Button(text='History', background_color=ROYAL)
        self.history_btn.bind(on_press=self.show_history)
        btn_row.add_widget(self.history_btn)

        self.qr_image = Image()
        self.main.add_widget(self.qr_image)

    def generate_qr(self, instance):
        data = self.input.text.strip()
        if not data:
            return
        qr = qrcode.QRCode(box_size=10, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

        data_io = io.BytesIO()
        img.save(data_io, format='png')
        data_io.seek(0)
        pil_image = PILImage.open(data_io)
        img_bytes = pil_image.tobytes()
        texture = Texture.create(size=pil_image.size)
        texture.blit_buffer(img_bytes, colorfmt='rgba', bufferfmt='ubyte')
        texture.flip_vertical()
        self.qr_image.texture = texture

        self.qr_history.append((data, img, texture))

    def save_qr(self, instance):
        if not self.qr_history:
            return
        data_str, pil_img, _ = self.qr_history[-1]

        def save_path(_):
            path = path_input.text.strip()
            if not path.endswith('.png'):
                path += '.png'
            try:
                pil_img.save(path)
                popup.dismiss()
            except Exception as e:
                print(f"Save failed: {e}")

        path_input = TextInput(text=f"{data_str}.png", multiline=False)
        save_btn = Button(text="Save", on_press=save_path, background_color=GREEN)
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(path_input)
        content.add_widget(save_btn)
        popup = Popup(title="Save QR", content=content, size_hint=(0.8, 0.4))
        popup.open()

    def load_qr(self, instance):
        filechooser = FileChooserListView(filters=['*.png'], size_hint=(1, 0.9))
        load_btn = Button(text="Load", background_color=BLUE)
        cancel_btn = Button(text="Cancel", background_color=PURPLE)
        content = BoxLayout(orientation='vertical')
        content.add_widget(filechooser)
        btn_row = BoxLayout(size_hint=(1, 0.1))
        btn_row.add_widget(load_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)
        popup = Popup(title="Load QR", content=content, size_hint=(0.9, 0.9))

        def do_load(_):
            for file_path in filechooser.selection:
                try:
                    pil_img = PILImage.open(file_path)
                    img_bytes = pil_img.tobytes()
                    texture = Texture.create(size=pil_img.size)
                    texture.blit_buffer(img_bytes, colorfmt='rgba', bufferfmt='ubyte')
                    texture.flip_vertical()
                    data_str = os.path.splitext(os.path.basename(file_path))[0]
                    self.qr_history.append((data_str, pil_img, texture))
                    self.qr_image.texture = texture
                    self.input.text = data_str
                except Exception as e:
                    print(f"Load failed: {e}")
            popup.dismiss()

        load_btn.bind(on_press=do_load)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def show_history(self, instance):
        if not self.qr_history:
            return
        content = BoxLayout(orientation='vertical')
        rv = RecycleView(size_hint=(1, 1))
        rv.viewclass = 'SelectableLabel'
        rv.data = [{'text': d[0]} for d in self.qr_history]
        rv_layout = SelectableRecycleBoxLayout(default_size=(None, 40), default_size_hint=(1, None), size_hint=(1, 1), orientation='vertical')
        rv.add_widget(rv_layout)
        rv.layout_manager = rv_layout
        content.add_widget(rv)
        self.history_rv = rv
        popup = Popup(title='QR Code History', content=content, size_hint=(0.8, 0.8))
        self.history_popup = popup
        popup.open()

    def load_history_item(self, index):
        if index < 0 or index >= len(self.qr_history):
            return
        data_str, pil_img, texture = self.qr_history[index]
        self.qr_image.texture = texture
        self.input.text = data_str
        self.history_popup.dismiss()


class QRApp(App):
    def build(self):
        return QRBox()


if __name__ == '__main__':
    QRApp().run()
