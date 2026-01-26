"""
QR code generation for passport verification.
"""
from io import BytesIO
import qrcode
from typing import Optional

def generate_qr_code(passport_id: str, base_url: str = "https://material-passport.app/passport/") -> bytes:
    """
    Generate QR code image as bytes.
    
    Args:
        passport_id: Unique passport identifier
        base_url: Base URL for passport viewing
    
    Returns:
        QR code image as bytes (PNG format)
    """
    try:
        # Create QR code URL
        qr_url = f"{base_url}{passport_id}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        
        # Generate QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        img_byte_arr = BytesIO()
        qr_image.save(img_byte_arr, format="PNG")
        img_bytes = img_byte_arr.getvalue()
        
        print(f"✓ Generated QR code for passport: {passport_id}")
        return img_bytes
        
    except Exception as e:
        print(f"✗ Error generating QR code: {e}")
        raise

def get_qr_code_url(passport_id: str, base_url: str) -> str:
    """
    Get the URL that the QR code should point to.
    
    Args:
        passport_id: Unique passport identifier
        base_url: Base URL for passport viewing
    
    Returns:
        URL as string
    """
    return f"{base_url}{passport_id}"
