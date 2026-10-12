from schemas import validate_benin_phone, detect_operator

# Numéros de test
numeros = [
    "0197123456",   # MTN (97)
    "0166123456",   # MTN (66)
    "0195123456",   # Moov (95)
    "0160123456",   # Moov (60)
    "0140123456",   # Celtiis (40)
    "0120123456",   # Celtiis (20)
    "0112123456",   # Invalide (12)
    "01971234",     # Trop court
    "0297123456",   # Ne commence pas par 01
]

for num in numeros:
    try:
        validated = validate_benin_phone(num)
        operator = detect_operator(validated)
        print(f"✅ {num} → {validated} ({operator})")
    except ValueError as e:
        print(f"❌ {num} → {e}")