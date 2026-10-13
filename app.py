import base64
import io
import math
import os
import random
from urllib.parse import quote

import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

TITLE = "AI-Based Personalized Cake Recommendation System with Design Assistance"

st.set_page_config(page_title=TITLE, page_icon="🎂", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #FAF6F0; }
header[data-testid="stHeader"] { background-color: #FAF6F0; }
h1, h2, h3 { color: #56392C; }
.subtitle { color: #806653; font-size: 17px; }
div.stButton > button, div.stFormSubmitButton > button {
    background-color: #704936; color: white; border-radius: 10px;
    border: none; min-height: 45px; font-weight: bold;
}
.price { color: #80552F; font-size: 26px; font-weight: bold; }
.footer { text-align: center; color: #806653; padding: 20px; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

st.title(TITLE)
st.markdown(
    '<p class="subtitle">Enter your cake details. We recommend the right '
    'cake and generate design images (top view and side view) that match '
    'your choices and your reference image.</p>',
    unsafe_allow_html=True,
)
st.divider()

# ---------------- Data ----------------
# name: (price per kg, look description for the image prompt)
FLAVOURS = {
    "Chocolate": (600, "chocolate flavour, dark chocolate frosting"),
    "Choco Truffle": (700, "chocolate truffle, glossy ganache"),
    "Double Chocolate": (750, "double chocolate, chocolate shavings"),
    "Death By Chocolate": (850, "rich dark chocolate, ganache drip and chocolate chunks"),
    "Belgian Chocolate": (900, "belgian dark chocolate, shiny ganache and chocolate curls"),
    "Choco Chip": (650, "chocolate chip cake, chocolate chips on cream"),
    "Dark Fantasy": (800, "dark fantasy, choco-filled cookies and dark chocolate"),
    "Kitkat": (850, "kitkat wafers around the cake with chocolate and gems"),
    "Oreo": (750, "oreo cookies and cream, oreo crumbs and cookie pieces"),
    "Cookies And Cream": (750, "cookies and cream, crushed cookies on white cream"),
    "Ferrero Rocher": (1100, "ferrero rocher chocolates, hazelnut and chocolate ganache"),
    "Raffaello": (1000, "raffaello coconut balls, white chocolate and coconut"),
    "Gems": (700, "colourful gems candy on chocolate cream"),
    "Lotus Biscoff": (900, "lotus biscoff, caramel drizzle and biscoff biscuits"),
    "Nutella Cheesecake": (1100, "nutella, hazelnut chocolate"),
    "Baskin Burnt Cheesecake": (1100, "burnt basque cheesecake, caramelised top"),
    "Strawberry": (600, "strawberry flavour, pink cream and fresh strawberries"),
    "Strawberry Cheesecake": (1000, "strawberry cheesecake, strawberry compote on top"),
    "Mango": (650, "mango flavour, fresh yellow mango cubes and mango cream"),
    "Mango Cheesecake": (1000, "mango cheesecake, mango glaze and mango pieces"),
    "Orange": (600, "orange flavour, orange slices and orange glaze"),
    "Pineapple": (600, "pineapple flavour, pineapple pieces and white cream"),
    "Lemon": (650, "lemon flavour, lemon slices and lemon glaze"),
    "Blackcurrant": (650, "blackcurrant flavour, purple berry glaze"),
    "Black Forest": (650, "black forest, cherries and chocolate shavings"),
    "White Forest": (650, "white forest, white chocolate shavings and cherries"),
    "Blueberry": (700, "blueberry flavour, blueberries and blue glaze"),
    "Blueberry Cheesecake": (1000, "blueberry cheesecake, blueberry compote"),
    "Mixed Fruit": (700, "fresh mixed fruits, kiwi, grapes, strawberry on cream"),
    "Fresh Fruit": (750, "fresh fruit cake, assorted fresh fruits and glaze"),
    "Blue Velvet": (750, "blue velvet sponge with cream cheese frosting"),
    "Red Velvet": (750, "red velvet sponge with cream cheese frosting"),
    "Vanilla": (550, "vanilla flavour, soft white cream"),
    "Vancho": (650, "vancho, vanilla and chocolate swirl"),
    "Butterscotch": (600, "butterscotch, caramel and crunchy praline"),
    "Salted Caramel": (800, "salted caramel, caramel drip and sea salt"),
    "Caramel": (700, "caramel flavour, golden caramel drizzle"),
    "Coffee Mocha": (750, "coffee mocha, coffee cream and cocoa dusting"),
    "Tiramisu": (900, "tiramisu, mascarpone cream and cocoa powder"),
    "Hazelnut": (850, "hazelnut flavour, roasted hazelnuts and praline"),
    "Almond Praline": (800, "almond praline, crunchy almond flakes"),
    "Pistachio": (950, "pistachio flavour, crushed pistachios and green cream"),
    "Kesar Pista": (950, "kesar pista, saffron strands and pistachio"),
    "Rasmalai": (800, "rasmalai flavour, saffron cream and pistachios"),
    "Gulab Jamun": (850, "gulab jamun flavour, syrup glaze and rose petals"),
    "Rose Milk": (700, "rose milk flavour, pink cream and rose petals"),
    "Paan": (800, "paan flavour, green cream and gulkand"),
    "Tender Coconut": (800, "tender coconut, coconut flakes and white cream"),
    "Honey Almond": (800, "honey almond, honey drizzle and almond slices"),
    "Banana Walnut": (700, "banana walnut, walnut pieces and caramel"),
    "Carrot": (750, "carrot cake, cream cheese frosting and walnuts"),
    "Plum Cake": (700, "rich plum fruit cake, dry fruits and icing"),
    "Matcha": (900, "matcha green tea, green cream and white chocolate"),
    "Cotton Candy": (800, "cotton candy flavour, pastel pink and blue cream swirls"),
}

# name: (price multiplier, look description for the image prompt)
TYPES = {
    "Normal Cake": (1.0, "a tall round layered sponge cake on a cake stand, frosted all around, not a cheesecake"),
    "Tiered Cake": (1.6, "a two tier sponge cake on a cake stand, not a cheesecake"),
    "Jar Cakes": (0.7, "layered dessert cake in a clear glass jar, visible cake and cream layers"),
    "Cheesecakes": (1.2, "a cheesecake with a biscuit base"),
    "Bento Cakes": (0.6, "a tiny mini bento lunchbox cake, 4 inch, in a small takeaway box, piped frosting, sponge cake, not a cheesecake"),
    "Tres Leches Cakes": (1.1, "a tres leches cake, milk soaked sponge slice with whipped cream topping"),
    "Dream Cakes": (1.3, "a dream cake, chocolate cake with creamy layers, glossy drip and rich decoration"),
    "Cookie Pies": (0.9, "a giant round cookie pie, baked cookie crust with cream and toppings"),
    "Brownie Cakes": (1.1, "a fudgy brownie cake with chocolate ganache on top"),
    "Tiramisu Cakes": (1.3, "a tiramisu cake, coffee soaked layers, mascarpone cream and cocoa dust"),
    "Mousse Cakes": (1.3, "a smooth mousse cake with a glossy mirror top"),
    "Cream Cakes": (1.0, "a classic round cream cake with swirled whipped cream"),
    "Ice Cream Cakes": (1.4, "an ice cream cake with layered ice cream and frozen toppings"),
    "Cake Pops": (0.8, "a set of cake pops on sticks, coated with candy melts"),
    "Cupcakes": (0.8, "a set of six frosted cupcakes on a tray"),
    "Swiss Roll Cakes": (0.9, "a sliced swiss roll cake with a cream spiral"),
    "Chiffon Cakes": (0.9, "a tall light chiffon cake with a soft airy crumb"),
    "Flourless Cakes": (1.2, "a dense flourless chocolate cake dusted with cocoa"),
    "Upside-Down Cakes": (1.0, "a pineapple upside-down cake with caramelised fruit on top"),
    "Tea Cakes": (0.7, "a simple loaf tea cake slices on a plate"),
    "Pull-Me-Up Cakes": (1.2, "a pull me up cake in a tub, layers of cake, cream and toppings"),
    "Pinata Cakes": (1.5, "a pinata cake with a chocolate shell filled with candies"),
}

OCCASIONS = ["Birthday", "Anniversary", "Wedding", "Baby Shower",
             "Engagement", "Farewell", "Graduation", "Just Because"]
SHAPES = ["Round", "Heart", "Square", "Rectangle"]
THEMES = ["Minimal", "Floral", "Vintage", "Drip Cake", "Elegant",
          "Cartoon / Kids", "Floral Pastel", "Rustic"]
COLOURS = ["White", "Pink", "Peach", "Brown", "Red", "Black", "Blue",
           "Purple", "Yellow", "Green", "Gold"]
FROSTINGS = ["Whipped Cream", "Buttercream", "Chocolate Ganache",
             "Fondant", "Cream Cheese", "Mirror Glaze"]
TOPPINGS = ["Fresh Fruits", "Chocolate Chips", "Sprinkles", "Edible Flowers",
            "Macarons", "Oreo Crumbs", "Nuts", "Gold Leaf", "Candles"]

# Reference pic colour naming
REF_COLOURS = {
    "peach": (245, 196, 170), "pink": (240, 160, 180),
    "blush pink": (245, 215, 215), "cream": (250, 240, 215),
    "white": (250, 250, 250), "red": (200, 40, 50),
    "chocolate brown": (110, 70, 50), "lavender": (200, 180, 230),
    "baby blue": (170, 205, 235), "mint green": (180, 225, 200),
    "yellow": (250, 225, 120),
}

FONT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "GreatVibes-Regular.ttf")
FONT_URL = ("https://github.com/google/fonts/raw/main/ofl/greatvibes/"
            "GreatVibes-Regular.ttf")


# ---------------- Helpers ----------------
def ensure_script_font():
    """Script font illa na auto-download pannum (oru dhadava mattum)."""
    if os.path.exists(FONT_FILE):
        return True
    try:
        r = requests.get(FONT_URL, timeout=20)
        if r.status_code == 200 and len(r.content) > 1000:
            with open(FONT_FILE, "wb") as f:
                f.write(r.content)
            return True
    except Exception:
        pass
    return False


def get_font(size):
    if ensure_script_font():
        try:
            return ImageFont.truetype(FONT_FILE, size)
        except Exception:
            pass
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    try:
        return ImageFont.load_default(size)
    except Exception:
        return ImageFont.load_default()


def fetch_image(url):
    for _ in range(2):
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 200 and \
                    r.headers.get("content-type", "").startswith("image"):
                return r.content
        except Exception:
            pass
    return None


def dominant_colour_name(img_bytes):
    """Reference cake nadula irukkura colour-a name-a kudukkum."""
    try:
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        w, h = img.size
        centre = img.crop((int(w * .3), int(h * .3),
                           int(w * .7), int(h * .7))).resize((50, 50))
        px = list(centre.getdata())
        avg = tuple(sum(p[i] for p in px) // len(px) for i in range(3))
        return min(REF_COLOURS, key=lambda n: sum(
            (a - b) ** 2 for a, b in zip(avg, REF_COLOURS[n])))
    except Exception:
        return None


def describe_reference(img_bytes):
    """
    Reference image-a vision model ku anuppi cake style description vaangum
    (free Pollinations vision endpoint). Fail aanaalum app work aagum.
    """
    try:
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img.thumbnail((512, 512))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        b64 = base64.b64encode(buf.getvalue()).decode()
        payload = {
            "model": "openai",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": (
                        "Describe only the cake in this photo in ONE short "
                        "sentence for an image generator: its shape, "
                        "frosting colour, frosting type, piping style, "
                        "decorations and finish. Do not mention any text, "
                        "words, table, plates or background.")},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{b64}"}},
                ],
            }],
            "max_tokens": 120,
        }
        r = requests.post("https://text.pollinations.ai/openai",
                          json=payload, timeout=45)
        if r.status_code == 200:
            text = r.json()["choices"][0]["message"]["content"].strip()
            return text[:300]
    except Exception:
        pass
    return None


def add_text(img_bytes, line1, line2):
    """
    Cake top mela, reference maari chinna elegant script text,
    box illama, cake nadula podum.
    """
    img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    lines = [t for t in (line1, line2) if t]
    if not lines:
        return img.convert("RGB")
    W, H = img.size

    # Cake colour paathu text colour decide (light cake -> dark text)
    cx0, cy0, cx1, cy1 = int(W * .35), int(H * .35), int(W * .65), int(H * .65)
    px = list(img.convert("RGB").crop((cx0, cy0, cx1, cy1))
              .resize((20, 20)).getdata())
    lum = sum(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2] for p in px) / len(px)
    if lum > 150:
        fill, shadow = (95, 62, 48, 255), (255, 255, 255, 90)
    else:
        fill, shadow = (255, 255, 255, 255), (0, 0, 0, 90)

    meas = ImageDraw.Draw(img)
    items = []
    for i, text in enumerate(lines):
        size = int(H * (0.10 if i == 0 else 0.07))
        font = get_font(size)
        while size > 14:
            box = meas.textbbox((0, 0), text, font=font)
            if box[2] - box[0] <= W * 0.50:
                break
            size -= 3
            font = get_font(size)
        box = meas.textbbox((0, 0), text, font=font)
        items.append((text, font, box[2] - box[0], box[3] - box[1], box))

    gap = int(H * 0.015)
    total_h = sum(it[3] for it in items) + gap * (len(items) - 1)
    y = int(H * 0.50) - total_h // 2

    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for text, font, w, h, box in items:
        x = (W - w) // 2 - box[0]
        d.text((x + 2, y - box[1] + 2), text, font=font, fill=shadow)
        d.text((x, y - box[1]), text, font=font, fill=fill)
        y += h + gap
    return Image.alpha_composite(img, layer).convert("RGB")


# ---------------- Form ----------------
st.header("🎨 Customise Your Cake")

with st.form("cake_form"):
    c1, c2 = st.columns(2)
    with c1:
        cake_type = st.selectbox("Cake Type", list(TYPES))
        flavour = st.selectbox("Cake Flavour", list(FLAVOURS))
        people = st.number_input("Number of People", 1, 200, 8)
        weight = st.selectbox(
            "Cake Size / Weight",
            ["Auto (recommend for me)", 0.5, 1.0, 1.5, 2.0, 3.0],
            format_func=lambda v: v if isinstance(v, str) else f"{v:g} kg",
        )
        occasion = st.selectbox("Occasion", OCCASIONS)
        shape = st.selectbox("Cake Shape", SHAPES)
    with c2:
        theme = st.selectbox("Design / Theme", THEMES)
        colour = st.selectbox("Cake Colour", COLOURS)
        frosting = st.selectbox("Frosting / Cream", FROSTINGS)
        toppings = st.multiselect("Toppings / Decorations", TOPPINGS,
                                  default=["Fresh Fruits"])
        topper = st.text_input("Cake Topper / Text",
                               placeholder="Example: The Chapmans")
        budget = st.number_input("Maximum Budget (₹)", 0, 20000, 2000, 100)

    note = st.text_input(
        "Customisation Message (printed on the cake if short)",
        placeholder="Example: I love you",
    )
    ref = st.file_uploader("Reference Cake Image (optional)",
