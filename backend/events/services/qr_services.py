"""
QR Code generation services
"""
import qrcode
import io
import base64


def generate_qr_code(event_code):
    """
    Generate a QR code for the event invitation.
    Returns a base64 encoded image string and the event URL.
    """
    # Build the full URL for the event with the specific server IP
    event_url = f"http://37.32.13.114:8000/events/{event_code}/"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(event_url)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 string
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return img_str, event_url
