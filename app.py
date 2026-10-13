import base64
import io
import math
import random
import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote

import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFilter, ImageFont

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
    'cake and generate top view and side view designs that match your '
    'choices and your reference image.</p>',
    unsafe_allow_html=True,
)
st.divider()

# ====================== DATA ======================
FLAVOURS = {
    "Chocolate": 600, "Choco Truffle": 700, "Double Chocolate": 750,
    "Lotus Biscoff": 900, "Strawberry": 600, "Mango": 650,
    "Orange": 600, "Nutella Cheesecake": 1100,
    "Baskin Burnt Cheesecake": 1100, "Vancho": 650,
    "Blackcurrant": 650, "Black Forest": 650, "White Forest": 650,
    "Blueberry": 700, "Blue Velvet": 750, "Red Velvet": 750,
    "Vanilla": 550, "Butterscotch": 600, "Rasmalai": 800,
    # ---- new flavours ----
    "Pineapple": 600, "Pista": 800, "Kitkat": 850, "Oreo": 750,
    "Ferrero Rocher": 1000, "Dates & Walnut": 800, "Mocha Coffee": 700,
    "Tiramisu": 950, "Caramel": 650, "Salted Caramel": 750,
    "Mixed Fruit": 700, "Fresh Fruit": 750, "Banana Walnut": 650,
    "Carrot": 700, "Lemon": 600, "Blueberry Cheesecake": 1100,
    "Strawberry Cheesecake": 1050, "Mango Cheesecake": 1050,
    "Oreo Cheesecake": 1100, "Lotus Biscoff Cheesecake": 1200,
    "Choco Chip": 650, "Gems Chocolate": 700, "Rose Milk": 700,
    "Paan": 750, "Coconut": 650, "Cookies & Cream": 750, "Brownie": 800,
    "Honey Almond": 750, "Pistachio Rose": 900, "Kunafa": 1000,
    "Pina Colada": 700, "Litchi": 700, "Hazelnut Praline": 900,
    "Biscoff Chocolate": 950, "Cotton Candy": 700, "Rainbow": 700,
    "Plum Cake": 700,
}
LOOK = {
    "Mango": "mango flavour, mango cream and fresh yellow mango cubes",
    "Strawberry": "strawberry flavour, pink cream and fresh strawberries",
    "Chocolate": "chocolate flavour, dark chocolate frosting",
    "Choco Truffle": "chocolate truffle, glossy ganache",
    "Double Chocolate": "double chocolate, chocolate shavings",
    "Lotus Biscoff": "lotus biscoff, caramel drizzle and biscoff biscuits",
    "Orange": "orange flavour, orange slices and orange glaze",
    "Blackcurrant": "blackcurrant flavour, purple berry glaze",
    "Black Forest": "black forest, cherries and chocolate shavings",
    "White Forest": "white forest, white chocolate shavings and cherries",
    "Blueberry": "blueberry flavour, blueberries and blue glaze",
    "Blue Velvet": "blue velvet sponge with cream cheese frosting",
    "Red Velvet": "red velvet sponge with cream cheese frosting",
    "Vanilla": "vanilla flavour, soft white cream",
    "Butterscotch": "butterscotch, caramel and crunchy praline",
    "Rasmalai": "rasmalai flavour, saffron cream and pistachios",
    "Vancho": "vancho, vanilla and chocolate swirl",
    "Nutella Cheesecake": "nutella, hazelnut chocolate",
    "Baskin Burnt Cheesecake": "burnt basque cheesecake, caramelised top",
    "Pineapple": "pineapple flavour, pineapple pieces and yellow cream",
    "Pista": "pistachio flavour, pistachio green cream and crushed pistachios",
    "Kitkat": "kitkat cake, chocolate wafer fingers around the sides",
    "Oreo": "oreo flavour, cookies and cream with oreo crumbs",
    "Ferrero Rocher": "ferrero rocher, hazelnut chocolate and golden chocolate balls",
    "Dates & Walnut": "dates and walnut, brown cream with walnuts",
    "Mocha Coffee": "mocha coffee flavour, coffee brown cream",
    "Tiramisu": "tiramisu, cocoa dusted cream",
    "Caramel": "caramel flavour, golden caramel drizzle",
    "Salted Caramel": "salted caramel, caramel drizzle and sea salt",
    "Mixed Fruit": "mixed fruit, assorted fresh fruit pieces",
    "Fresh Fruit": "fresh fruit cake, kiwi, strawberry, grapes",
    "Banana Walnut": "banana walnut, banana slices and walnuts",
    "Carrot": "carrot cake, cream cheese frosting and walnuts",
    "Lemon": "lemon flavour, lemon glaze and lemon slices",
    "Blueberry Cheesecake": "blueberry cheesecake, blueberry compote",
    "Strawberry Cheesecake": "strawberry cheesecake, strawberry compote",
    "Mango Cheesecake": "mango cheesecake, mango glaze",
    "Oreo Cheesecake": "oreo cheesecake, oreo crumbs",
    "Lotus Biscoff Cheesecake": "biscoff cheesecake, biscoff spread and biscuits",
    "Choco Chip": "choco chip, chocolate chips in cream",
    "Gems Chocolate": "chocolate cake decorated with colourful gems candies",
    "Rose Milk": "rose milk flavour, pale pink cream and rose petals",
    "Paan": "paan flavour, green cream and gulkand",
    "Coconut": "coconut flavour, white cream and coconut flakes",
    "Cookies & Cream": "cookies and cream, crushed cookies",
    "Brownie": "brownie cake, fudgy chocolate",
    "Honey Almond": "honey almond, honey glaze and almond flakes",
    "Pistachio Rose": "pistachio and rose, pistachios and rose petals",
    "Kunafa": "kunafa, golden crispy kunafa strands and pistachio",
    "Pina Colada": "pina colada, pineapple and coconut",
    "Litchi": "litchi flavour, litchi fruits and pale cream",
    "Hazelnut Praline": "hazelnut praline, praline crunch and hazelnuts",
    "Biscoff Chocolate": "chocolate and biscoff, biscoff biscuits",
    "Cotton Candy": "cotton candy, pastel pink and blue swirls",
    "Rainbow": "rainbow sponge layers with colourful cream",
    "Plum Cake": "plum cake, dark fruit cake with dry fruits",
}
TYPES = {"Normal Cake": 1.0, "Bento Cake": 0.6, "Cupcakes": 0.8,
         "Tiered Cake": 1.6, "Cheesecake": 1.2, "Jar Cake": 0.5}

SHAPES = {"Round": 1.0, "Heart": 1.1, "Square": 1.05, "Rectangle": 1.05}
SHAPE_WORD = {
    "Round": "round",
    "Heart": "heart-shaped (clear heart outline with two lobes on top and "
             "a point at the bottom, NOT round)",
    "Square": "square",
    "Rectangle": "rectangular",
}


def subject_for(cake_type, shape):
    s = SHAPE_WORD[shape]
    return {
        "Normal Cake": f"a single tier {s} layered sponge cake on a plain "
                       f"white cake stand, frosted all around",
        "Bento Cake": f"a small 4 inch {s} bento cake with piped frosting",
        "Cupcakes": "a set of six frosted cupcakes on a tray",
        "Tiered Cake": f"a two tier {s} sponge cake on a cake stand",
        "Cheesecake": f"a {s} cheesecake with a biscuit base",
        "Jar Cake": "layered dessert cakes served in clear glass jars",
    }[cake_type]


OCCASIONS = ["Birthday", "Anniversary", "Wedding", "Baby Shower",
             "Engagement", "Farewell", "Graduation", "Valentine's Day",
             "Just Because"]
THEMES = ["Minimal", "Floral", "Vintage", "Drip Cake", "Elegant",
          "Cartoon / Kids", "Floral Pastel", "Rustic", "Lambeth / Heart Retro"]
COLOURS = ["White", "Ivory", "Peach", "Nude / Beige", "Pink", "Baby Pink",
           "Lavender", "Mint Green", "Brown", "Red", "Black", "Blue",
           "Purple", "Yellow", "Green", "Gold"]
FROSTINGS = ["Whipped Cream", "Buttercream", "Chocolate Ganache",
             "Fondant", "Cream Cheese", "Mirror Glaze"]
PIPING = {
    "Auto / follow reference": "",
    "Smooth & clean (no piping)": "smooth clean frosting with a flat top and no piping",
    "Shell border": "piped shell border around the top edge",
    "Rosette border": "piped rosette border around the top edge",
    "Ruffle border": "ruffled piped border around the edge",
    "Vintage lambeth piping": "vintage lambeth style piped scalloped borders",
    "Floral piping": "piped buttercream flowers on top and edge",
}
TOPPINGS = ["Fresh Fruits", "Chocolate Chips", "Sprinkles", "Edible Flowers",
            "Macarons", "Oreo Crumbs", "Nuts", "Gold Leaf", "Candles",
            "Cherries", "Pearls", "Chocolate Drizzle"]
TOPPER_STYLES = {
    "White acrylic script": ((255, 255, 255, 255), (0, 0, 0, 90)),
    "Gold script": ((201, 162, 39, 255), (0, 0, 0, 90)),
    "Chocolate piped script": ((92, 52, 36, 255), (255, 255, 255, 60)),
    "Black acrylic script": ((25, 25, 25, 255), (255, 255, 255, 50)),
    "Pink icing script": ((226, 112, 146, 255), (0, 0, 0, 50)),
}

FONT_URLS = (
    "https://github.com/google/fonts/raw/main/ofl/greatvibes/GreatVibes-Regular.ttf",
    "https://github.com/google/fonts/raw/main/ofl/allura/Allura-Regular.ttf",
)
VIEWS = {
    "top": "overhead top-down view looking straight down at the cake top, "
           "cake centred in frame, plain empty top surface",
    "side": "side-on three-quarter angle view at eye level, cake centred "
            "with empty space above it, plain empty top",
}
NO_TEXT = "no text, no letters, no writing, no watermark"


# ====================== HELPERS ======================
@st.cache_resource(show_spinner=False)
def script_font_bytes():
    for url in FONT_URLS:
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200 and len(r.content) > 10000:
                return r.content
        except Exception:
            pass
    return None


def get_font(size):
    data = script_font_bytes()
    if data:
        try:
            return ImageFont.truetype(io.BytesIO(data), size)
        except Exception:
            pass
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        "C:/Windows/Fonts/segoesc.ttf",
        "C:/Windows/Fonts/ariali.ttf",
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
    for _ in range(3):
        try:
            r = requests.get(url, timeout=90)
            if r.status_code == 200 and \
                    r.headers.get("content-type", "").startswith("image"):
                return r.content
        except Exception:
            pass
    return None


PALETTE = {
    "white": (245, 245, 245), "ivory": (250, 244, 225),
    "soft peach": (246, 205, 180), "nude beige": (225, 200, 175),
    "light pink": (248, 200, 210), "dark pink": (225, 110, 140),
    "red": (190, 30, 40), "brown": (110, 70, 50),
    "dark chocolate": (60, 35, 25), "yellow": (245, 215, 90),
    "lavender": (200, 180, 225), "mint green": (185, 225, 200),
    "blue": (110, 160, 220), "black": (25, 25, 25), "gold": (205, 165, 60),
}


def colour_hint(img_bytes):
    """Fallback if vision model is not reachable: dominant colour of centre."""
    try:
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        w, h = img.size
        crop = img.crop((w // 4, h // 4, 3 * w // 4, 3 * h // 4)).resize((1, 1))
        r, g, b = crop.getpixel((0, 0))
        name = min(PALETTE, key=lambda k: sum(
            (a - c) ** 2 for a, c in zip(PALETTE[k], (r, g, b))))
        return f"{name} coloured frosting"
    except Exception:
        return ""


REF_Q = (
    "Describe only the physical cake in this image for an image generator. "
    "Reply with ONE line of comma-separated phrases, max 60 words, covering: "
    "shape (heart, round, square), number of tiers, exact frosting colour "
    "(e.g. soft peach), frosting texture, piping style and where it is "
    "(e.g. shell border piped around the top edge), toppings or decorations "
    "(write 'no toppings, flat clean top' if none), cake stand and background "
    "colour. Ignore any text or lettering on the cake. No other words."
)


def describe_reference(img_bytes):
    """Vision model reads the reference cake so the generator can copy it."""
    try:
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img.thumbnail((768, 768))
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=85)
        b64 = base64.b64encode(buf.getvalue()).decode()
        payload = {
            "model": "openai",
            "max_tokens": 220,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": REF_Q},
                    {"type": "image_url",
                     "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                ],
            }],
        }
        r = requests.post("https://text.pollinations.ai/openai",
                          json=payload, timeout=60)
        if r.status_code == 200:
            txt = r.json()["choices"][0]["message"]["content"]
            txt = re.sub(r"\s+", " ", txt).strip()
            if len(txt) > 15:
                return txt[:380]
    except Exception:
        pass
    return colour_hint(img_bytes)


def build_prompt(view, cake_type, shape, flavour, theme, colour, frosting,
                 piping, toppings, occasion, ref_desc, extra):
    parts = [
        f"Professional food photography, {VIEWS[view]}, of "
        f"{subject_for(cake_type, shape)}",
    ]
    if ref_desc:
        parts.append("copy this reference design exactly: " + ref_desc)
    parts += [
        f"{colour.lower()} coloured cake with {frosting.lower()} frosting",
        LOOK.get(flavour, flavour.lower() + " flavour"),
        f"{theme.lower()} style",
    ]
    if PIPING[piping]:
        parts.append(PIPING[piping])
    if toppings:
        parts.append("decorated only with " + ", ".join(t.lower() for t in toppings))
    elif not ref_desc:
        parts.append("clean simple top with no toppings")
    if extra:
        parts.append(extra)
    parts.append(f"for a {occasion.lower()} celebration, soft studio "
                 f"lighting, high detail, {NO_TEXT}")
    return ", ".join(parts)[:1500]


def make_url(prompt, seed, model="flux"):
    return ("https://image.pollinations.ai/prompt/" + quote(prompt)
            + f"?width=768&height=768&nologo=true&model={model}&seed={seed}")


def overlay_text(img_bytes, line1, line2, style, cx, cy, scale, angle):
    """Script text written ON the cake (no box), like an acrylic topper."""
    img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    lines = [t for t in (line1, line2) if t]
    if not lines:
        return img.convert("RGB")
    W, H = img.size
    fill, shadow = TOPPER_STYLES[style]
    probe = ImageDraw.Draw(img)
    items = []
    for i, text in enumerate(lines):
        max_w = W * (0.46 if i == 0 else 0.36) * scale
        size = max(14, int(H * (0.12 if i == 0 else 0.07) * scale))
        font = get_font(size)
        while size > 12:
            b = probe.textbbox((0, 0), text, font=font)
            if b[2] - b[0] <= max_w:
                break
            size -= 3
            font = get_font(size)
        items.append((text, font, probe.textbbox((0, 0), text, font=font)))
    gap = int(H * 0.012)
    pad = int(H * 0.04)
    tw = max(b[2] - b[0] for _, _, b in items)
    th = sum(b[3] - b[1] for _, _, b in items) + gap * (len(items) - 1)
    layer = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y = pad
    for text, font, b in items:
        w, h = b[2] - b[0], b[3] - b[1]
        d.text(((layer.width - w) // 2 - b[0], y - b[1]), text,
               font=font, fill=fill)
        y += h + gap
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", layer.size, shadow[:3] + (0,))
    sh.putalpha(layer.split()[3].point(lambda a: int(a * shadow[3] / 255)))
    sh = sh.filter(ImageFilter.GaussianBlur(max(2, H // 250)))
    px = int(cx / 100 * W - layer.width / 2)
    py = int(cy / 100 * H - layer.height / 2)
    off = max(2, H // 300)
    img.paste(sh, (px + off, py + off), sh)
    img.paste(layer, (px, py), layer)
    return img.convert("RGB")


def to_png(img):
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


# ====================== FORM ======================
st.header("🎨 Customise Your Cake")

with st.form("cake_form"):
    c1, c2 = st.columns(2)
    with c1:
        cake_type = st.selectbox("Cake Type", list(TYPES))
        flavour = st.selectbox("Cake Flavour", sorted(FLAVOURS))
        people = st.number_input("Number of People", 1, 200, 8)
        weight = st.selectbox(
            "Cake Size / Weight",
            ["Auto (recommend for me)", 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0],
            format_func=lambda v: v if isinstance(v, str) else f"{v:g} kg",
        )
        occasion = st.selectbox("Occasion", OCCASIONS)
        shape = st.selectbox("Cake Shape", list(SHAPES))
        piping = st.selectbox("Piping / Border Style", list(PIPING))
    with c2:
        theme = st.selectbox("Design / Theme", THEMES)
        colour = st.selectbox("Cake Colour", COLOURS)
        frosting = st.selectbox("Frosting / Cream", FROSTINGS)
        toppings = st.multiselect(
            "Toppings / Decorations (leave empty for a clean top)", TOPPINGS)
        topper = st.text_input("Cake Topper / Text",
                               placeholder="Example: The Chapmans")
        topper_style = st.selectbox("Topper Style", list(TOPPER_STYLES))
        budget = st.number_input("Maximum Budget (₹)", 0, 20000, 2000, 100)

    note = st.text_input(
        "Customisation Message (printed under the topper, keep it short)",
        placeholder="Example: I love you",
    )
    extra = st.text_input(
        "Extra design details (optional)",
        placeholder="Example: pearls around the border, small bow on the side",
    )
    ref = st.file_uploader(
        "Reference Cake Image (optional - design will follow this)",
        type=["png", "jpg", "jpeg"])
    go = st.form_submit_button("Generate My Cake Design",
                               use_container_width=True)

# ====================== GENERATE ======================
if go:
    rec_weight = max(0.5, math.ceil(people / 8 * 2) / 2)
    final_weight = rec_weight if isinstance(weight, str) else weight
    price = round(FLAVOURS[flavour] * TYPES[cake_type] * SHAPES[shape]
                  * final_weight)
    price += 50 * len(toppings) + (100 if topper.strip() else 0)

    ref_bytes = ref.getvalue() if ref is not None else None
    with st.spinner("Reading reference & designing top + side view... "
                    "10-60 seconds"):
        ref_desc = describe_reference(ref_bytes) if ref_bytes else ""
        seed = random.randint(1, 999999)
        args = (cake_type, shape, flavour, theme, colour, frosting, piping,
                toppings, occasion, ref_desc, extra.strip())
        p_top = build_prompt("top", *args)
        p_side = build_prompt("side", *args)
        with ThreadPoolExecutor(2) as ex:
            f1 = ex.submit(fetch_image, make_url(p_top, seed))
            f2 = ex.submit(fetch_image, make_url(p_side, seed))
            top_img, side_img = f1.result(), f2.result()

    st.session_state["res"] = dict(
        top=top_img, side=side_img, ref=ref_bytes, ref_desc=ref_desc,
        line1=topper.strip(),
        line2=note.strip() if len(note.strip()) <= 40 else "",
        style=topper_style, price=price, budget=budget, people=people,
        rec_weight=rec_weight, final_weight=final_weight, occasion=occasion,
        flavour=flavour, cake_type=cake_type, shape=shape, theme=theme,
        colour=colour, frosting=frosting, piping=piping, toppings=toppings,
        note=note.strip(), long_note=len(note.strip()) > 40,
    )

# ====================== RESULT ======================
res = st.session_state.get("res")
if res:
    st.divider()
    st.header("✨ Your Personalised Cake")

    with st.expander("✏️ Text position / size adjust pannu (no regenerate)"):
        show_side = st.checkbox("Show text on side view too", True)
        a, b = st.columns(2)
        with a:
            st.caption("Top view")
            tx = st.slider("Left-Right %", 0, 100, 50, key="tx")
            ty = st.slider("Up-Down %", 0, 100, 50, key="ty")
            ts = st.slider("Size", 0.4, 1.8, 1.0, 0.05, key="ts")
            tr = st.slider("Tilt (degrees)", -40, 40, -8, key="tr")
        with b:
            st.caption("Side view")
            sx = st.slider("Left-Right %", 0, 100, 50, key="sx")
            sy = st.slider("Up-Down %", 0, 100, 36, key="sy")
            ss = st.slider("Size", 0.4, 1.8, 0.7, 0.05, key="ss")
            sr = st.slider("Tilt (degrees)", -40, 40, -6, key="sr")

    v1, v2 = st.columns(2)
    outputs = {}
    with v1:
        st.subheader("Top View")
        if res["top"]:
            outputs["top"] = overlay_text(res["top"], res["line1"],
                                          res["line2"], res["style"],
                                          tx, ty, ts, tr)
            st.image(outputs["top"], use_container_width=True)
            st.download_button("Download top view", to_png(outputs["top"]),
                               "cake_top.png", "image/png", key="dl_top")
        else:
            st.warning("Top view server busy. Press Generate again.")
    with v2:
        st.subheader("Side View")
        if res["side"]:
            if show_side:
                outputs["side"] = overlay_text(res["side"], res["line1"],
                                               res["line2"], res["style"],
                                               sx, sy, ss, sr)
            else:
                outputs["side"] = Image.open(
                    io.BytesIO(res["side"])).convert("RGB")
            st.image(outputs["side"], use_container_width=True)
            st.download_button("Download side view", to_png(outputs["side"]),
                               "cake_side.png", "image/png", key="dl_side")
        else:
            st.warning("Side view server busy. Press Generate again.")

    st.caption("AI-generated designs. Text is added exactly as you typed it "
               "(spelling always correct). Press Generate again for a new "
               "variation.")
    if res["long_note"]:
        st.info("Message 40 characters ku mela irukku, so image la print "
                "aagala. Short ah vechuko.")

    st.subheader("Recommendation")
    d1, d2 = st.columns(2)
    with d1:
        st.write(f"**Occasion:** {res['occasion']}")
        st.write(f"**Cake:** {res['flavour']} {res['cake_type']}")
        st.write(f"**Shape / Theme:** {res['shape']}, {res['theme']}")
        st.write(f"**Colour / Frosting:** {res['colour']}, {res['frosting']}")
        st.write(f"**Piping:** {res['piping']}")
        st.write(f"**Toppings:** {', '.join(res['toppings']) or 'None'}")
        if res["line1"]:
            st.write(f"**Topper text:** {res['line1']} ({res['style']})")
        if res["note"]:
            st.write(f"**Message:** {res['note']}")
    with d2:
        st.write(f"**People:** {res['people']}")
        st.write(f"**Recommended size:** {res['rec_weight']:g} kg for "
                 f"{res['people']} people")
        st.write(f"**Selected size:** {res['final_weight']:g} kg")
        if res["final_weight"] < res["rec_weight"]:
            st.warning("Selected size may be small for this many people.")
        st.markdown(f"<p class='price'>Estimated price: ₹{res['price']:,}</p>",
                    unsafe_allow_html=True)
        if res["price"] > res["budget"]:
            st.warning("This is above your budget. Try a smaller size, "
                       "fewer toppings or a cheaper flavour.")
        else:
            st.success("Within your budget.")

    if res["ref"]:
        st.subheader("Reference vs Generated")
        r1, r2 = st.columns(2)
        with r1:
            st.write("**Your reference image:**")
            st.image(res["ref"], use_container_width=True)
        with r2:
            st.write("**What the AI understood from the reference:**")
            st.write(res["ref_desc"] or "Could not read the reference.")

st.markdown(f"<div class='footer'>{TITLE}</div>", unsafe_allow_html=True)
