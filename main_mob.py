# Upgraded QR Code App with a Fully Unified UI

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout # Import FloatLayout for the image container
from kivy.uix.dropdown import DropDown
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
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.metrics import dp

# Import graphics instructions to draw the background
from kivy.graphics import Color, Rectangle

import qrcode
from PIL import Image as PILImage
import io
import os
import webbrowser

# --- Unified Color Scheme (Fine-tuned to match the screenshot) ---
BACKGROUND_COLOR = (0.12, 0.20, 0.35, 1)     # Medium navy blue

# Button colors
PRIMARY_COLOR = (0.25, 0.45, 0.85, 1)        # Bright sky blue
ACCENT_COLOR = (0.15, 0.65, 0.95, 1)         # Poppy cyan-blue for Generate
SECONDARY_COLOR = (0.6, 0.5, 0.9, 1)         # Brighter violet-blue

# Input background
INPUT_BG_COLOR = (0.18, 0.28, 0.45, 1)       # Lighter desaturated blue
Window.clearcolor = BACKGROUND_COLOR

class SelectableLabel(RecycleDataViewBehavior, Label):
    # ... (No changes in this class)
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
            app_root = App.get_running_app().root
            app_root.load_history_item(index)

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    # ... (No changes in this class)
    pass

class QRBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(15)

        self.qr_history = []

        # --- Top Action Bar ---
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        self.add_widget(top_bar)

        self.dropdown = DropDown()
        link_btn = Button(text='LinkedIn', size_hint_y=None, height=dp(44), background_color=PRIMARY_COLOR)
        link_btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
        self.dropdown.add_widget(link_btn)

        gh_btn = Button(text='GitHub', size_hint_y=None, height=dp(44), background_color=SECONDARY_COLOR)
        gh_btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
        self.dropdown.add_widget(gh_btn)
        
        menu_button = Button(text='Menu', size_hint_x=0.25, background_color=PRIMARY_COLOR)
        menu_button.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=self.on_menu_select)

        self.save_btn = Button(text='Save', background_color=PRIMARY_COLOR, size_hint_x=0.25)
        self.save_btn.bind(on_press=self.save_qr)
        self.load_btn = Button(text='Load', background_color=PRIMARY_COLOR, size_hint_x=0.25)
        self.load_btn.bind(on_press=self.load_qr)
        self.history_btn = Button(text='History', background_color=PRIMARY_COLOR, size_hint_x=0.25)
        self.history_btn.bind(on_press=self.show_history)
        
        top_bar.add_widget(menu_button)
        top_bar.add_widget(self.save_btn)
        top_bar.add_widget(self.load_btn)
        top_bar.add_widget(self.history_btn)

        # --- Main Content Area ---
        input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        self.add_widget(input_layout)

        self.input = TextInput(
            hint_text='Enter text or URL',
            size_hint_x=0.7,
            multiline=False,
            background_color=INPUT_BG_COLOR,
            foreground_color=(1, 1, 1, 0.8), # Slightly off-white text
            halign="center",   # <-- centers text horizontally
        )
        def update_padding(instance, value):
            instance.padding_y = [(instance.height - instance.line_height) / 2, 0]

        # Bind the function so padding updates when height or line height changes
        self.input.bind(height=update_padding, line_height=update_padding)
        input_layout.add_widget(self.input)

        self.gen_btn = Button(text='Generate', background_color=ACCENT_COLOR, size_hint_x=0.3)
        self.gen_btn.bind(on_press=self.generate_qr)
        input_layout.add_widget(self.gen_btn)

        image_container = FloatLayout(size_hint_y=1)

# 2. Add a background rectangle to the CONTAINER's canvas.
        with image_container.canvas.before:
            Color(rgba=BACKGROUND_COLOR)  # unified blue background
            self.bg_rect = Rectangle(size=image_container.size, pos=image_container.pos)

        # 3. Bind the rectangle's size and pos to the container's size and pos.
        def update_bg_rect(instance, value):
            self.bg_rect.pos = instance.pos
            self.bg_rect.size = instance.size
        image_container.bind(pos=update_bg_rect, size=update_bg_rect)

        # 4. Create the Image widget, but make it transparent until QR is loaded
        self.qr_image = Image(
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            allow_stretch=True,
            keep_ratio=True
        )
        self.qr_image.color = (1, 1, 1, 0)  # hide white placeholder until QR is generated

        # 5. Add the Image to the container, and the container to the main layout.
        image_container.add_widget(self.qr_image)
        self.add_widget(image_container)
     

    def on_menu_select(self, instance, value):
        # ... (No changes in this method)
        if value == 'LinkedIn':
            webbrowser.open('https://linkedin.com/in/yourprofile')
        elif value == 'GitHub':
            webbrowser.open('https://github.com/yourprofile')
        elif value =="Docs":
            webbrowser.open('https://github.com/yourprofile/docs') # TK

    def generate_qr(self, instance):
        data = self.input.text.strip()
        if not data:
            return

        qr = qrcode.QRCode(box_size=10, border=2)
        qr.add_data(data)
        qr.make(fit=True)

        # Use unified blue background
        bg_r, bg_g, bg_b, _ = BACKGROUND_COLOR
        pil_bg_color = (int(bg_r * 255), int(bg_g * 255), int(bg_b * 255))

        # Make QR white foreground on blue background
        img = qr.make_image(fill_color="white", back_color=pil_bg_color).convert("RGBA")

        data_io = io.BytesIO()
        img.save(data_io, format='png')
        data_io.seek(0)
        pil_image = PILImage.open(data_io)
        img_bytes = pil_image.tobytes()
        texture = Texture.create(size=pil_image.size)
        texture.blit_buffer(img_bytes, colorfmt='rgba', bufferfmt='ubyte')
        texture.flip_vertical()
        self.qr_image.texture = texture
        self.qr_image.color = (1, 1, 1, 1)  # make QR visible once generated
        self.qr_history.append((data, img, texture))

    def save_qr(self, instance):
        # ... (No changes in this method)
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

        path_input = TextInput(text=f"{data_str}.png", multiline=False, size_hint_y=None, height=dp(40))
        save_btn = Button(text="Save", on_press=save_path, background_color=ACCENT_COLOR, size_hint_y=None, height=dp(40))
        
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        content.add_widget(path_input)
        content.add_widget(save_btn)
        
        popup = Popup(title="Save QR Code", content=content, size_hint=(0.9, None), height=dp(150))
        popup.open()

    def load_qr(self, instance):
        # ... (No changes in this method)
        filechooser = FileChooserListView(filters=['*.png'], size_hint_y=0.8)
        btn_row = BoxLayout(size_hint_y=None, height=dp(80), spacing=dp(10))

        load_btn = Button(text="Load", background_color=PRIMARY_COLOR, size_hint_y=1)
        cancel_btn = Button(text="Cancel", background_color=SECONDARY_COLOR, size_hint_y=1)
        
        content = BoxLayout(orientation='vertical')
        content.add_widget(filechooser)
        
        btn_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        btn_row.add_widget(load_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        popup = Popup(title="Load QR Code", content=content, size_hint=(0.9, 0.9))

        def do_load(_):
            if not filechooser.selection:
                popup.dismiss()
                return
            file_path = filechooser.selection[0]
            try:
                pil_img = PILImage.open(file_path)
                img_bytes = pil_img.tobytes()
                texture = Texture.create(size=pil_image.size)
                texture.blit_buffer(img_bytes, colorfmt='rgba', bufferfmt='ubyte')
                texture.flip_vertical()
                data_str = os.path.splitext(os.path.basename(file_path))[0]
                self.qr_history.append((data_str, pil_img, texture))
                self.qr_image.texture = texture
                self.qr_image.color = (1, 1, 1, 1)  # make QR visible once loaded
                self.input.text = data_str
            except Exception as e:
                print(f"Load failed: {e}")
            popup.dismiss()

        load_btn.bind(on_press=do_load)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def show_history(self, instance):
        # ... (No changes in this method)
        if not self.qr_history:
            return
        content = BoxLayout(orientation='vertical')
        rv = RecycleView(viewclass='SelectableLabel')
        rv.data = [{'text': d[0]} for d in self.qr_history]
        
        rv_layout = SelectableRecycleBoxLayout(
            default_size=(None, dp(44)),
            default_size_hint=(1, None),
            size_hint_y=None,
            orientation='vertical'
        )
        rv_layout.bind(minimum_height=rv_layout.setter('height'))
        rv.add_widget(rv_layout)
        rv.layout_manager = rv_layout
        
        content.add_widget(rv)
        
        popup = Popup(title='QR Code History', content=content, size_hint=(0.9, 0.8))
        self.history_popup = popup
        popup.open()

    def load_history_item(self, index):
        # ... (No changes in this method)
        if 0 <= index < len(self.qr_history):
            data_str, _, texture = self.qr_history[index]
            self.qr_image.texture = texture
            self.input.text = data_str
            self.history_popup.dismiss()


class QRApp(App):
    def build(self):
        return QRBox()


if __name__ == '__main__':
    QRApp().run()