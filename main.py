from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="OLX Nuasxa API", description="E'lonlar va reklama platformasi uchun backend")

# Ma'lumotlar modeli (Ma'lumotlar bazasi o'rniga hozircha vaqtinchalik xotira)
class Elon(BaseModel):
    id: int
    sarlavha: str
    tavsif: str
    narx: float
    valyuta: str = "UZS"
    kategoriya: str
    manzil: str
    telefon: str
    rasm_url: Optional[str] = None
    yaratilgan_vaqt: datetime = datetime.now()

# Vaqtinchalik ma'lumotlar bazasi (Buni keyinchalik PostgreSQL yoki MongoDB ga ulash kerak)
elonlar_bazasi: List[Elon] = [
    {
        "id": 1,
        "sarlavha": "iPhone 15 Pro Max sotiladi",
        "tavsif": "Holati ideal, 256GB, rangi Natural Titanium. Karobka-dokument bor.",
        "narx": 12000000,
        "valyuta": "UZS",
        "kategoriya": "Elektronika",
        "manzil": "Toshkent shahar, Chilonzor",
        "telefon": "+998901234567",
        "rasm_url": "https://example.com/iphone15.jpg",
        "yaratilgan_vaqt": datetime.now()
    }
]

# 1. Barcha e'lonlarni olish (Kategoriya bo'yicha saralash filtri bilan)
@app.get("/elonlar/", response_model=List[Elon])
def barcha_elonlar(kategoriya: Optional[str] = None):
    if kategoriya:
        filtr_elonlar = [e for e in elonlar_bazasi if e["kategoriya"].lower() == kategoriya.lower()]
        return filtr_elonlar
    return elonlar_bazasi

# 2. Bitta e'lonni ID bo'yicha olish
@app.get("/elonlar/{elon_id}", response_model=Elon)
def bitta_elon(elon_id: int):
    for elon in elonlar_bazasi:
        if elon["id"] == elon_id:
            return elon
    raise HTTPException(status_code=404, detail="E'lon topilmadi")

# 3. Yangi e'lon qo'shish
@app.post("/elonlar/yaratish/", response_model=Elon)
def elon_yaratish(yangi_elon: Elon):
    # ID takrorlanmasligini tekshirish
    for elon in elonlar_bazasi:
        if elon["id"] == yangi_elon.id:
            raise HTTPException(status_code=400, detail="Bu ID dagi e'lon allaqachon mavjud")
    
    elonlar_bazasi.append(yangi_elon.dict())
    return yangi_elon

# 4. E'lonni o'chirish
@app.delete("/elonlar/ochirish/{elon_id}")
def elon_ochirish(elon_id: int):
    for index, elon in enumerate(elonlar_bazasi):
        if elon["id"] == elon_id:
            elonlar_bazasi.pop(index)
            return {"xabar": "E'lon muvaffaqiyatli o'chirildi"}
    raise HTTPException(status_code=404, detail="E'lon topilmadi")
