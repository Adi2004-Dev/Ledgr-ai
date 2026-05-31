import pytesseract
from PIL import Image
import re


pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

def extract_expense_from_image(image_path):
    """
    Extracts transaction amount from UPI screenshots (PhonePe, GPay, etc.)[cite: 49, 76].
    """
    img = Image.open(image_path)
    raw_text = pytesseract.image_to_string(img)
    
    
    clean_text = raw_text.replace(',', '') 
    
    
    amount_match = re.search(r'(?:₹|Rs\.?|INR)\s*(\d+(?:\.\d{2})?)', clean_text, re.IGNORECASE)
    
    if amount_match:
        amount = float(amount_match.group(1))
    else:
        
        numbers = re.findall(r'\b\d{1,5}\b', clean_text)
        amount = float(numbers[0]) if numbers else 0.00
        
    return {"amount": amount, "raw_text": raw_text}
