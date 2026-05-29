import sys
from pathlib import Path

# Allow importing the app package when running from backend/
sys.path.insert(0, str(Path(__file__).parent))

from app.database import engine, SessionLocal
from app.models import Base, Product

# Ensure tables exist
Base.metadata.create_all(bind=engine)

products_data = [
    {"id":"ts-001","code":"MO-001","name":"Pool Club Tee","type":"tshirt","price":1290,"stock":15,"art_class":"art-sunrise","emoji":"🌊","image":"poolclubtee.png","description":"Screen-printed on 220gsm cotton"},
    {"id":"ts-002","code":"MO-002","name":"Pulse Beam Tee","type":"tshirt","price":1290,"stock":10,"art_class":"art-waterlily","emoji":"💧","image":"pulsetee.png","description":"Screen-printed on 220gsm cotton, oversized fit"},
    {"id":"ts-003","code":"DE-001","name":"Windy Club Tee","type":"tshirt","price":1390,"stock":8,"art_class":"art-ballet","emoji":"🐾","image":"windyclubtee.png","description":"Organic cotton, oversized fit"},
    {"id":"ts-004","code":"RE-001","name":"Pop Girl Tee","type":"tshirt","price":1290,"stock":0,"art_class":"art-boating","emoji":"🎀","image":"pgtee.png","description":"Screen-printed on 220gsm cotton, oversized fit"},
    {"id":"pn-001","code":"MO-003","name":"Pop Girl Pin Pack","type":"pin","price":550,"stock":30,"art_class":"art-waterlily","emoji":"💧","image":"pg pin pack.png","description":"Acrylic Pin"},
    {"id":"pn-002","code":"MO-004","name":"Windy Club Pin","type":"pin","price":550,"stock":22,"art_class":"art-sunrise","emoji":"🌅","image":"windy pin.png","description":"1.5\" cloisonné enamel"},
    {"id":"pn-003","code":"DE-002","name":"Happy Pin","type":"pin","price":500,"stock":18,"art_class":"art-ballet","emoji":"🎀","image":"happy pin.png","description":"Soft enamel, rubber clasp"},
    {"id":"pn-004","code":"PI-001","name":"Wrumple Pin","type":"pin","price":500,"stock":14,"art_class":"art-parasol","emoji":"☂️","image":"wrumple pin.png","description":"Acrylic Enamel Pin"},
    {"id":"st-001","code":"MO-005","name":"Pop Girl Sticker Pack","type":"sticker","price":290,"stock":50,"art_class":"art-garden","emoji":"🌷","image":"popgirl stickerpck.png","description":"Holo vinyl, 4-pack"},
    {"id":"st-002","code":"CA-001","name":"Funky Sticker Pack","type":"sticker","price":290,"stock":40,"art_class":"art-rouen","emoji":"⛪","image":"funky stickerpck.png","description":"Matte archival vinyl"},
    {"id":"st-003","code":"PI-002","name":"PG Funny Sticker Pack","type":"sticker","price":250,"stock":60,"art_class":"art-boulevard","emoji":"🌃","image":"funnypg stickerpck.png","description":"Clear vinyl, waterproof"},
    {"id":"st-004","code":"MO-006","name":"Despair Sticker","type":"sticker","price":290,"stock":0,"art_class":"art-bridge","emoji":"🌉","image":"despair sticker.png","description":"Clear vinyl, waterproof"},
    {"id":"ac-001","code":"DE-003","name":"Graphic Art Card","type":"artcard","price":750,"stock":20,"art_class":"art-ballet","emoji":"🩰","image":"graphic ap.png","description":"Letterpress on cotton rag"},
    {"id":"ac-002","code":"MO-007","name":"Haystacks Art Card","type":"artcard","price":750,"stock":15,"art_class":"art-haystacks","emoji":"🌾","image":"wormholeap.png","description":"Giclée, numbered edition"},
    {"id":"ac-003","code":"RE-002","name":"Data Art Card","type":"artcard","price":700,"stock":10,"art_class":"art-parasol","emoji":"☂️","image":"dataap.png","description":"Silkscreen, 2-colour print"},
    {"id":"ac-004","code":"IR-001","name":"Farm Girl Cards","type":"artcard","price":700,"stock":7,"art_class":"art-iris","emoji":"🌸","image":"farmgirlap.png","description":"Risograph, hand-signed"},
]

db = SessionLocal()
count = db.query(Product).count()
if count == 0:
    for p in products_data:
        db.add(Product(**p))
    db.commit()
    print(f"Seeded {len(products_data)} products.")
else:
    print(f"Products already exist ({count} found). Skipping seed.")
db.close()
