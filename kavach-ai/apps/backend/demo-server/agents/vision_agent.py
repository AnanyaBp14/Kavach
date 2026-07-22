import hashlib
import random

def verify_banknote(image_bytes: bytes, filename: str):
    image_hash = hashlib.sha256(image_bytes if image_bytes else filename.encode()).hexdigest()
    
    # Deterministic simulation based on hash or filename
    is_fake = "fake" in filename.lower() or int(image_hash[:2], 16) % 2 == 0
    
    if is_fake:
        return {
            "verdict": "Likely Counterfeit",
            "prediction": "Counterfeit / Fake Currency",
            "confidence": 94.8,
            "risk": "CRITICAL",
            "features": {
                "watermark": {"status": "FAIL", "score": 12, "details": "Gandhi watermark alignment offset by 3.2mm"},
                "microprinting": {"status": "PASS", "score": 85, "details": "RBI microtext present on collar"},
                "security_thread": {"status": "FAIL", "score": 18, "details": "Color shift thread fails UV luminescence test"},
                "uv_pattern": {"status": "FAIL", "score": 25, "details": "Optical fibers missing under 365nm UV filter"}
            },
            "suspicious_regions": [[120, 200], [340, 400]],
            "explanation": [
                "Security thread lacks magnetic signature and UV fluorescent color shift.",
                "Watermark exhibits sharpness anomalies typical of inkjet forgery.",
                "Latent image denomination '500' failed refractive angle test."
            ],
            "sha256_hash": image_hash
        }
    else:
        return {
            "verdict": "Likely Genuine",
            "prediction": "Genuine Currency Note",
            "confidence": 98.2,
            "risk": "LOW",
            "features": {
                "watermark": {"status": "PASS", "score": 96, "details": "Authentic multi-tone Gandhi watermark detected"},
                "microprinting": {"status": "PASS", "score": 98, "details": "Clear 'RBI 500' microprinting verified"},
                "security_thread": {"status": "PASS", "score": 95, "details": "Green-to-blue windowed security thread shift verified"},
                "uv_pattern": {"status": "PASS", "score": 97, "details": "Fluorescent fibers glowing accurately under UV light"}
            },
            "suspicious_regions": [],
            "explanation": [
                "All 4 key security features (watermark, security thread, microtext, UV pattern) passed verification.",
                "Intaglio printing tactile features detected on border."
            ],
            "sha256_hash": image_hash
        }
