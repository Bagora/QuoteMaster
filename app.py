from flask import Flask, render_template, send_file, session
import requests
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for session to work

@app.route('/')
def home():
    # Fetch a random quote from an API
    response = requests.get('https://zenquotes.io/api/random')
    data = response.json()
    quote = data[0]['q'] + " - " + data[0]['a']
    
    # Store the quote in the session
    session['current_quote'] = quote
    
    return render_template('index.html', quote=quote)

@app.route('/download-image')
def download_image():
    # Get the current quote from the session
    quote = session.get('current_quote', "No quote available")  # Fallback text if no quote

    # Create an image with a size of 800x800
    img_size = (800, 800)
    img = Image.new('RGB', img_size, color=(255, 255, 255))
    d = ImageDraw.Draw(img)

    # Define a larger font size and use a bold font
    font_size = 48  # Adjust the font size
    font = ImageFont.truetype("Roboto-Bold.ttf", font_size)  # Ensure to use a bold font

    # Draw a colorful background
    for i in range(img_size[0]):
        for j in range(img_size[1]):
            r = int((i / img_size[0]) * 255)
            g = int((j / img_size[1]) * 255)
            b = 150  # Fixed blue value for a colorful mix
            d.point((i, j), fill=(r, g, b))

    # Define margins
    margin = 50
    text_area = (margin, margin, img_size[0] - margin, img_size[1] - margin)

    # Wrap text and draw it
    wrapped_lines = []
    words = quote.split()
    line = ""

    for word in words:
        # Check if adding the word exceeds the text area
        test_line = line + word + " "
        text_bbox = d.textbbox((0, 0), test_line, font=font)
        if text_bbox[2] - text_bbox[0] > text_area[2] - text_area[0]:  # If line exceeds width
            wrapped_lines.append(line.strip())
            line = word + " "  # Start new line with the current word
        else:
            line = test_line  # Continue building the line

    # Add the last line
    if line:
        wrapped_lines.append(line.strip())

    # Calculate total height for centering
    line_height = font.getmetrics()[1] + 40  # Increased padding for line height
    total_height = line_height * len(wrapped_lines)
    start_y = (img.height - total_height) / 2  # Center the text vertically

    for i, line in enumerate(wrapped_lines):
        # Get text bounding box
        bbox = d.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (img.width - text_width) / 2  # Center horizontally
        d.text((text_x, start_y + i * line_height), line, fill=(0, 0, 0), font=font)  # Black text

    # Save the image to a bytes buffer
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')  # Save as PNG
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='quote.png')

if __name__ == '__main__':
    app.run(debug=True)
