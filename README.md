# QR Code Generator App

A modern, feature-rich QR code generator built with Python and Kivy, featuring a unified navy blue theme and comprehensive QR code management capabilities.

## Features

### Core Functionality
- **QR Code Generation**: Convert any text or URL into a QR code instantly
- **Save & Load**: Save generated QR codes as PNG files and load existing ones
- **History Management**: Keep track of all generated QR codes in an interactive history view
- **Menu Integration**: Quick access to social media profiles (LinkedIn, GitHub)

### User Interface
- Modern navy blue color scheme with sky blue accents
- Responsive design that adapts to different screen sizes
- Intuitive button layout with clear visual hierarchy
- Centered text input with placeholder hints
- Full-screen QR code display with proper scaling

### Advanced Features
- **File Browser**: Built-in file chooser for loading existing QR codes
- **History Browser**: Scrollable list of previously generated QR codes
- **Dynamic Backgrounds**: Unified color scheme throughout all UI elements
- **Error Handling**: Graceful handling of file operations and user input

## Requirements

```
kivy>=2.1.0
qrcode[pil]>=7.0
Pillow>=9.0.0
```

## Installation

1. **Install Python dependencies**:
   ```bash
   pip install kivy qrcode[pil] Pillow
   ```

2. **Download the application**:
   ```bash
   # Save the code as qr_app.py
   ```

3. **Run the application**:
   ```bash
   python qr_app.py
   ```

## Usage

### Generating QR Codes
1. Enter your text or URL in the input field
2. Click the **Generate** button
3. Your QR code will appear in the main display area

### Saving QR Codes
1. Generate a QR code first
2. Click the **Save** button
3. Enter your desired filename (`.png` will be added automatically)
4. Click **Save** to save the file

### Loading QR Codes
1. Click the **Load** button
2. Browse and select a PNG file containing a QR code
3. Click **Load** to display the QR code

### Viewing History
1. Click the **History** button to see all generated QR codes
2. Click on any item in the history to reload that QR code
3. The history persists during your current session

### Menu Options
- Click **Menu** to access quick links to social media profiles
- Links can be customized by modifying the `on_menu_select` method

## Customization

### Color Scheme
The app uses a unified color scheme defined at the top of the file:
- `BACKGROUND_COLOR`: Main navy blue background
- `PRIMARY_COLOR`: Sky blue for primary buttons
- `ACCENT_COLOR`: Cyan-blue for the Generate button
- `SECONDARY_COLOR`: Violet-blue for secondary elements
- `INPUT_BG_COLOR`: Darker blue for input fields

### Social Media Links
Update the URLs in the `on_menu_select` method:
```python
def on_menu_select(self, instance, value):
    if value == 'LinkedIn':
        webbrowser.open('https://linkedin.com/in/yourprofile')
    elif value == 'GitHub':
        webbrowser.open('https://github.com/yourprofile')
```

### QR Code Styling
QR codes are generated with:
- White foreground on blue background
- 10px box size for optimal clarity
- 2px border for clean appearance

## Technical Details

### Architecture
- **Main App Class**: `QRApp` - Entry point and app configuration
- **Main Widget**: `QRBox` - Contains all UI elements and logic
- **Custom Widgets**: 
  - `SelectableLabel` - Interactive history items
  - `SelectableRecycleBoxLayout` - Scrollable history container

### File Structure
- QR codes are saved as PNG files with RGBA color format
- History is stored in memory during the session
- Textures are cached for efficient display

### Dependencies
- **Kivy**: Cross-platform GUI framework
- **qrcode**: QR code generation library
- **Pillow (PIL)**: Image processing and manipulation
- **webbrowser**: System browser integration

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all required packages are installed
2. **File Save Failures**: Check write permissions for the target directory
3. **Image Loading Issues**: Verify the PNG file contains a valid QR code
4. **Display Problems**: Try running with `--fullscreen` or adjust window size

### Performance Tips
- Large QR codes may take a moment to generate
- History is limited by available system memory
- Close unused popups to maintain smooth performance

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to fork this project and submit pull requests for improvements or bug fixes. Areas for enhancement include:
- Database persistence for history
- QR code scanning capabilities  
- Additional export formats
- Batch processing features
- Theme customization options