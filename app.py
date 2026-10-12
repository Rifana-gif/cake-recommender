import math
import random
from urllib.parse import quote

import streamlit as st

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
TYPES = {"Normal Cake": 1.0, "Bento Cake": 0.6, "Cupcakes": 0.8,
         "Tiered Cake": 1.6, "Cheesecake": 1.2}
OCCASIONS = ["Birthday", "Anniversary", "Wedding", "Baby Shower",
             "Engagement", "Farewell", "Graduation", "Just Because"]
SHAPES = ["Round", "Heart", "Square", "Rectangle", "Bento Round"]
THEMES = ["Minimal", "Floral", "Vintage", "Drip Cake", "Elegant",
          "Cartoon / Kids", "Floral Pastel", "Rustic"]
COLOURS = ["White", "Pink", "Brown", "Red", "Black", "Blue",
           "Purple", "Yellow", "Green", "Gold"]
FROSTINGS = ["Whipped Cream", "Buttercream", "Chocolate Ganache",
             "Fondant", "Cream Cheese", "Mirror Glaze"]
TOPPINGS = ["Fresh Fruits", "Chocolate Chips", "Sprinkles", "Edible Flowers",
            "Macarons", "Oreo Crumbs", "Nuts", "Gold Leaf", "Candles"]

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
                               placeholder="Example: Happy Birthday")
        budget = st.number_input("Maximum Budget (₹)", 0, 20000, 2000, 100)

    note = st.text_area("Customisation Message",
                        placeholder="Any special request for the baker")
    ref = st.file_uploader("Reference Cake Image (optional)",
                           type=["png", "jpg", "jpeg"])
    go = st.form_submit_button("Generate My Cake Design",
                               use_container_width=True)

# ---------------- Logic ----------------
if go:
    # weight recommendation: about 8 servings per kg
    rec_weight = max(0.5, math.ceil(people / 8 * 2) / 2)
    final_weight = rec_weight if isinstance(weight, str) else weight
    price = round(FLAVOURS[flavour] * TYPES[cake_type] * final_weight)
    price += 50 * len(toppings)

    st.divider()
    st.header("✨ Your Personalised Cake")

    left, right = st.columns(2)

    with left:
        # Build the image prompt only from the user's own choices
        top_text = f', with the text "{topper.strip()}" written on top' \
            if topper.strip() else ""
        top_list = ", ".join(t.lower() for t in toppings) or "no extra toppings"
        prompt = (
            f"Professional food photography of a {shape.lower()} "
            f"{flavour.lower()} {cake_type.lower()}, {theme.lower()} theme, "
            f"{colour.lower()} colour, {frosting.lower()} frosting, "
            f"decorated with {top_list}{top_text}, "
            f"for a {occasion.lower()} celebration, studio lighting, "
            f"on a cake stand, high detail"
        )
        seed = random.randint(1, 999999)
        url = (
            "https://image.pollinations.ai/prompt/"
            + quote(prompt)
            + f"?width=768&height=768&nologo=true&seed={seed}"
        )
        st.subheader("Generated Design")
        st.image(url, use_container_width=True)
        st.caption("AI-generated image. Text on the cake may not be exact. "
                   "Press the button again for a new variation.")
        st.markdown(f"[Open image in new tab]({url})")

    with right:
        st.subheader("Recommendation")
        st.write(f"**Occasion:** {occasion}")
        st.write(f"**Cake:** {flavour} {cake_type}")
        st.write(f"**Shape / Theme:** {shape}, {theme}")
        st.write(f"**Colour / Frosting:** {colour}, {frosting}")
        st.write(f"**Toppings:** {', '.join(toppings) or 'None'}")
        if topper.strip():
            st.write(f"**Topper text:** {topper}")
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

        if note.strip():
            st.info(f"Your note: {note}")
        if ref is not None:
            st.write("**Your reference image:**")
            st.image(ref, use_container_width=True)

st.markdown(f"<div class='footer'>{TITLE}</div>", unsafe_allow_html=True)
