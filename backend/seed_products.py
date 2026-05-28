import sys
from pathlib import Path

# Allow importing the app package when running from backend/
sys.path.insert(0, str(Path(__file__).parent))

from app.database import engine, SessionLocal
from app.models import Base, Product

# Ensure tables exist
Base.metadata.create_all(bind=engine)

products_data = [
    {"id":"ts-001","code":"MO-001","name":"Impression Sunrise Tee","type":"tshirt","price":1290,"stock":15,"art_class":"art-sunrise","emoji":"🌅","image":"ts-sunrise.jpg","description":"Screen-printed on 220gsm cotton"},
    {"id":"ts-002","code":"MO-002","name":"Water Lilies Tee","type":"tshirt","price":1290,"stock":10,"art_class":"art-waterlily","emoji":"💧","image":"ts-waterlily.jpg","description":"Heavyweight jersey, unisex cut"},
    {"id":"ts-003","code":"DE-001","name":"Ballet Tee","type":"tshirt","price":1390,"stock":8,"art_class":"art-ballet","emoji":"🎀","image":"ts-ballet.jpg","description":"Organic cotton, oversized fit"},
    {"id":"ts-004","code":"RE-001","name":"Regatta Tee","type":"tshirt","price":1290,"stock":0,"art_class":"art-boating","emoji":"⛵","image":"ts-regatta.jpg","description":"Premium ring-spun cotton"},
    {"id":"pn-001","code":"MO-003","name":"Waterlily Pin","type":"pin","price":550,"stock":30,"art_class":"art-waterlily","emoji":"💧","image":"pn-waterlily.jpg","description":"Hard enamel, gold plating"},
    {"id":"pn-002","code":"MO-004","name":"Sunrise Pin","type":"pin","price":550,"stock":22,"art_class":"art-sunrise","emoji":"🌅","image":"pn-sunrise.jpg","description":"1.5\" cloisonné enamel"},
    {"id":"pn-003","code":"DE-002","name":"Ballet Pin","type":"pin","price":500,"stock":18,"art_class":"art-ballet","emoji":"🎀","image":"pn-ballet.jpg","description":"Soft enamel, rubber clasp"},
    {"id":"pn-004","code":"PI-001","name":"Parasol Pin","type":"pin","price":500,"stock":14,"art_class":"art-parasol","emoji":"☂️","image":"pn-parasol.jpg","description":"Hard enamel, silver plating"},
    {"id":"st-001","code":"MO-005","name":"Garden Sticker Pack","type":"sticker","price":290,"stock":50,"art_class":"art-garden","emoji":"🌷","image":"st-garden.jpg","description":"Holo vinyl, 4-pack"},
    {"id":"st-002","code":"CA-001","name":"Cathedral Sticker","type":"sticker","price":290,"stock":40,"art_class":"art-rouen","emoji":"⛪","image":"st-cathedral.jpg","description":"Matte archival vinyl"},
    {"id":"st-003","code":"PI-002","name":"Boulevard Sticker","type":"sticker","price":250,"stock":60,"art_class":"art-boulevard","emoji":"🌃","image":"st-boulevard.jpg","description":"Clear vinyl, waterproof"},
    {"id":"st-004","code":"MO-006","name":"Bridge Sticker Pack","type":"sticker","price":290,"stock":0,"art_class":"art-bridge","emoji":"🌉","image":"st-bridge.jpg","description":"Foil-finish vinyl pack"},
    {"id":"ac-001","code":"DE-003","name":"Ballet Art Card","type":"artcard","price":750,"stock":20,"art_class":"art-ballet","emoji":"🩰","image":"ac-ballet.jpg","description":"Letterpress on cotton rag"},
    {"id":"ac-002","code":"MO-007","name":"Haystacks Art Card","type":"artcard","price":750,"stock":15,"art_class":"art-haystacks","emoji":"🌾","image":"ac-haystacks.jpg","description":"Giclée, numbered edition"},
    {"id":"ac-003","code":"RE-002","name":"Parasol Art Card","type":"artcard","price":700,"stock":10,"art_class":"art-parasol","emoji":"☂️","image":"ac-parasol.jpg","description":"Silkscreen, 5-colour print"},
    {"id":"ac-004","code":"IR-001","name":"Iris Art Card","type":"artcard","price":700,"stock":7,"art_class":"art-iris","emoji":"🌸","image":"ac-iris.jpg","description":"Risograph, hand-signed"},
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
