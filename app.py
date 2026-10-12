import io
import math
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
    'cake and generate a design image that matches your choices.</p>',
    unsafe_allow_html=True,
)
st.divider()

# ---------------- Data ----------------
FLAVOURS = {
    "Chocolate": 600, "Choco Truffle": 700, "Double Chocolate": 750,
    "Lotus Biscoff": 900, "Strawberry": 600, "Mango": 650,
    "Orange": 600, "Nutella Cheesecake": 1100,
    "Baskin Burnt Cheesecake": 1100, "Vancho": 650,
    "Blackcurrant": 650, "Black Forest": 650, "White Forest": 650,
    "Blueberry": 700, "Blue Velvet": 750, "Red Velvet": 750,
    "Vanilla": 550, "Butterscotch": 600, "Rasmalai": 800,
}
LOOK = {
    "Mango": "mango flavour, fresh yellow mango cubes and mango cream",
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
}
TYPES = {"Normal Cake": 1.0, "Bento Cake": 0.6, "Cupcakes": 0.8,
         "Tiered Cake": 1.6, "Cheesecake": 1.2}
TYPE_LOOK = {
    "Normal Cake": "a tall round layered sponge cake on a cake stand, "
                   "frosted all around, not a cheesecake",
    "Bento Cake": "a tiny mini bento lunchbox cake, 4 inch, in a small "
                  "takeaway box, piped frosting, sponge cake, "
                  "not a cheesecake",
    "Cupcakes": "a set of six frosted cupcakes on a tray",
    "Tiered Cake": "a two tier sponge cake on a cake stand, not a cheesecake",
    "Cheesecake": "a cheesecake with a biscuit base",
}
OCCASIONS = ["Birthday", "Anniversary", "Wedding", "Baby Shower",
             "Engagement", "Farewell", "Graduation", "Just Because"]
SHAPES = ["Round", "Heart", "Square", "Rectangle"]
THEMES = ["Minimal", "Floral", "Vintage", "Drip Cake", "Elegant",
          "Cartoon / Kids", "Floral Pastel", "Rustic"]
COLOURS = ["White", "Pink", "Brown", "Red", "Black", "Blue",
           "Purple", "Yellow", "Green", "Gold"]
FROSTINGS = ["Whipped Cream", "Buttercream", "Chocolate Ganache",
             "Fondant", "Cream Cheese", "Mirror Glaze"]
TOPPINGS = ["Fresh Fruits", "Chocolate Chips", "Sprinkles", "Edible Flowers",
            "Macarons", "Oreo Crumbs", "Nuts", "Gold Leaf", "Candles"]


# ---------------- Helpers ----------------
def get_font(size):
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


def add_text(img_bytes, line1, line2):
    img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    lines = [t for t in (line1, line2) if t]
    if not lines:
        return img.convert("RGB")
    W, H = img.size
    draw_main = ImageDraw.Draw(img)
    items = []
    for i, text in enumerate(lines):
        size = H // 11 if i == 0 else H // 16
        font = get_font(size)
        while size > 12:
            box = draw_main.textbbox((0, 0), text, font=font)
            if box[2] - box[0] <= W * 0.86:
                break
            size -= 4
            font = get_font(size)
        box = draw_main.textbbox((0, 0), text, font=font)
        items.append((text, font, box[2] - box[0], box[3] - box[1]))
    gap = H // 60
    pad = H // 40
    total_h = sum(it[3] for it in items) + gap * (len(items) - 1)
    max_w = max(it[2] for it in items)
    bw, bh = max_w + pad * 3, total_h + pad * 2
    x0 = (W - bw) // 2
    y0 = int(H * 0.60)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), radius=pad,
                        fill=(255, 250, 240, 215))
    y = y0 + pad
    for text, font, w, h in items:
        d.text(((W - w) // 2, y), text, font=font, fill=(86, 57, 44, 255))
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
                               placeholder="Example: Happy Anniversary")
        budget = st.number_input("Maximum Budget (₹)", 0, 20000, 2000, 100)

    note = st.text_input(
        "Customisation Message (printed on the cake if short)",
        placeholder="Example: I love you",
    )
    ref = st.file_uploader("Reference Cake Image (optional)",
                           type=["png", "jpg", "jpeg"])
    go = st.form_submit_button("Generate My Cake Design",
                               use_container_width=True)

# ---------------- Result ----------------
if go:
    rec_weight = max(0.5, math.ceil(people / 8 * 2) / 2)
    final_weight = rec_weight if isinstance(weight, str) else weight
    price = round(FLAVOURS[flavour] * TYPES[cake_type] * final_weight)
    price += 50 * len(toppings)

    st.divider()
    st.header("✨ Your Personalised Cake")
    left, right = st.columns(2)

    with left:
        top_list = ", ".join(t.lower() for t in toppings) or "no extra toppings"
        prompt = (
            f"Professional food photography of {TYPE_LOOK[cake_type]}, "
            f"{LOOK.get(flavour, flavour.lower() + ' flavour')}, "
            f"{shape.lower()} shape, {theme.lower()} theme, "
            f"{colour.lower()} coloured cake, covered with "
            f"{frosting.lower()}, decorated with {top_list}, "
            f"for a {occasion.lower()} celebration, "
            f"plain empty top with no writing, studio lighting, high detail"
        )
        seed = random.randint(1, 999999)
        url = (
            "https://image.pollinations.ai/prompt/" + quote(prompt)
            + f"?width=768&height=768&nologo=true&model=flux&seed={seed}"
        )

        st.subheader("Generated Design")
        with st.spinner("Designing your cake... this can take 10-40 seconds"):
            data = fetch_image(url)

        line1 = topper.strip()
        line2 = note.strip() if len(note.strip()) <= 40 else ""

        if data:
            try:
                final = add_text(data, line1, line2)
                st.image(final, use_container_width=True)
            except Exception:
                st.image(data, use_container_width=True)
        else:
            st.warning("Image server is busy. Press the button again.")
            st.image(url, use_container_width=True)

        st.caption("AI-generated design. The text is added exactly as you "
                   "typed it. Press the button again for a new variation.")

    with right:
        st.subheader("Recommendation")
        st.write(f"**Occasion:** {occasion}")
        st.write(f"**Cake:** {flavour} {cake_type}")
        st.write(f"**Shape / Theme:** {shape}, {theme}")
        st.write(f"**Colour / Frosting:** {colour}, {frosting}")
        st.write(f"**Toppings:** {', '.join(toppings) or 'None'}")
        if topper.strip():
            st.write(f"**Topper text:** {topper}")
        if note.strip():
            st.write(f"**Message:** {note}")
        st.write(f"**People:** {people}")
        st.write(f"**Recommended size:** {rec_weight:g} kg for {people} people")
        st.write(f"**Selected size:** {final_weight:g} kg")
        st.markdown(f"<p class='price'>Estimated price: ₹{price:,}</p>",
                    unsafe_allow_html=True)
        if price > budget:
            st.warning("This is above your budget. Try a smaller size, "
                       "fewer toppings or a cheaper flavour.")
        else:
            st.success("Within your budget.")
        if ref is not None:
            st.write("**Your reference image:**")
            st.image(ref, use_container_width=True)

st.markdown(f"<div class='footer'>{TITLE}</div>", unsafe_allow_html=True)
