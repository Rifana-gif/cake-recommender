import streamlit as st

# ==================================================
# PROJECT CONFIGURATION
# ==================================================

PROJECT_TITLE = (
    "AI-Based Personalized Cake Recommendation "
    "System with Design Assistance"
)

st.set_page_config(
    page_title=PROJECT_TITLE,
    page_icon="🎂",
    layout="wide"
)

# ==================================================
# PAGE DESIGN
# ==================================================

st.markdown("""
<style>
.stApp {
    background-color: #FAF6F0;
}

header[data-testid="stHeader"] {
    background-color: #FAF6F0;
}

h1, h2, h3 {
    color: #56392C;
}

.subtitle {
    color: #806653;
    font-size: 17px;
}

div.stButton > button {
    background-color: #704936;
    color: white;
    border-radius: 10px;
    border: none;
    min-height: 45px;
    font-weight: bold;
}

div.stButton > button:hover {
    background-color: #503326;
    color: white;
}

.cake-price {
    color: #80552F;
    font-size: 23px;
    font-weight: bold;
}

.footer {
    text-align: center;
    color: #806653;
    padding: 20px;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# WEBSITE HEADER
# ==================================================

st.title(PROJECT_TITLE)

st.markdown(
    '<p class="subtitle">'
    'Personalize your cake preferences and discover '
    'matching cake designs.'
    '</p>',
    unsafe_allow_html=True
)

st.divider()

# ==================================================
# CAKE DATASET
# Existing image URLs; no image-generation API
# ==================================================

cakes = [
    {
        "name": "Chocolate Dream",
        "flavour": "Chocolate",
        "colour": "Brown",
        "shape": "Round",
        "style": "Drip Cake",
        "price": 650,
        "image": (
            "https://images.unsplash.com/"
            "photo-1578985545062-69928b1d9587?w=700"
        )
    },
    {
        "name": "Classic White Cake",
        "flavour": "Vanilla",
        "colour": "White",
        "shape": "Round",
        "style": "Minimal",
        "price": 550,
        "image": (
            "https://images.unsplash.com/"
            "photo-1535141192574-5d4897c12636?w=700"
        )
    },
    {
        "name": "Pink Celebration",
        "flavour": "Strawberry",
        "colour": "Pink",
        "shape": "Round",
        "style": "Floral",
        "price": 600,
        "image": (
            "https://images.unsplash.com/"
            "photo-1464349095431-e9a21285b5f3?w=700"
        )
    },
    {
        "name": "Vintage Celebration",
        "flavour": "Vanilla",
        "colour": "Pink",
        "shape": "Heart",
        "style": "Vintage",
        "price": 750,
        "image": (
            "https://images.unsplash.com/"
            "photo-1551879400-111a9087cd86?w=700"
        )
    },
    {
        "name": "Red Velvet Special",
        "flavour": "Red Velvet",
        "colour": "Red",
        "shape": "Round",
        "style": "Elegant",
        "price": 750,
        "image": (
            "https://images.unsplash.com/"
            "photo-1586788680434-30d324b2d46f?w=700"
        )
    },
    {
        "name": "Butterscotch Delight",
        "flavour": "Butterscotch",
        "colour": "Brown",
        "shape": "Round",
        "style": "Minimal",
        "price": 600,
        "image": (
            "https://images.unsplash.com/"
            "photo-1565958011703-44f9829ba187?w=700"
        )
    },
    {
        "name": "Black Forest Classic",
        "flavour": "Black Forest",
        "colour": "Brown",
        "shape": "Round",
        "style": "Drip Cake",
        "price": 650,
        "image": (
            "https://images.unsplash.com/"
            "photo-1578985545062-69928b1d9587?w=700"
        )
    },
    {
        "name": "Elegant Chocolate",
        "flavour": "Chocolate",
        "colour": "White",
        "shape": "Round",
        "style": "Elegant",
        "price": 700,
        "image": (
            "https://images.unsplash.com/"
            "photo-1606313564200-e75d5e30476c?w=700"
        )
    },
    {
        "name": "Chocolate Bento",
        "flavour": "Chocolate",
        "colour": "Brown",
        "shape": "Bento",
        "style": "Minimal",
        "price": 350,
        "image": (
            "https://images.unsplash.com/"
            "photo-1578985545062-69928b1d9587?w=700"
        )
    },
    {
        "name": "Strawberry Special",
        "flavour": "Strawberry",
        "colour": "White",
        "shape": "Round",
        "style": "Elegant",
        "price": 650,
        "image": (
            "https://images.unsplash.com/"
            "photo-1464349095431-e9a21285b5f3?w=700"
        )
    },
    {
        "name": "Blackcurrant Style",
        "flavour": "Blackcurrant",
        "colour": "Purple",
        "shape": "Round",
        "style": "Elegant",
        "price": 650,
        "image": (
            "https://images.unsplash.com/"
            "photo-1535141192574-5d4897c12636?w=700"
        )
    },
    {
        "name": "Rasmalai Celebration",
        "flavour": "Rasmalai",
        "colour": "Yellow",
        "shape": "Round",
        "style": "Floral",
        "price": 650,
        "image": (
            "https://images.unsplash.com/"
            "photo-1535141192574-5d4897c12636?w=700"
        )
    }
]

# ==================================================
# CUSTOMER PREFERENCES
# ==================================================

st.header("🎨 Customize Your Cake")

with st.form("cake_customization_form"):

    col1, col2 = st.columns(2)

    with col1:
        flavour = st.selectbox(
            "Cake Flavour",
            [
                "Any Flavour",
                "Chocolate",
                "Vanilla",
                "Strawberry",
                "Black Forest",
                "Butterscotch",
                "Red Velvet",
                "Blackcurrant",
                "Rasmalai"
            ]
        )

        colour = st.selectbox(
            "Preferred Colour",
            [
                "Any Colour",
                "White",
                "Pink",
                "Brown",
                "Red",
                "Black",
                "Blue",
                "Purple",
                "Yellow"
            ]
        )

        shape = st.selectbox(
            "Cake Shape",
            [
                "Any Shape",
                "Round",
                "Heart",
                "Square",
                "Bento"
            ]
        )

    with col2:
        style = st.selectbox(
            "Design Style",
            [
                "Any Style",
                "Minimal",
                "Floral",
                "Vintage",
                "Drip Cake",
                "Elegant"
            ]
        )

        weight = st.selectbox(
            "Cake Weight",
            [0.5, 1.0, 1.5, 2.0],
            format_func=lambda value: f"{value:g} kg"
        )

        budget = st.number_input(
            "Maximum Budget (₹)",
            min_value=0,
            value=1000,
            step=100
        )

    message = st.text_input(
        "Message on Cake",
        placeholder="Example: Happy Birthday"
    )

    submitted = st.form_submit_button(
        "Find My Cake Designs",
        use_container_width=True
    )

# ==================================================
# RECOMMENDATION SYSTEM
# ==================================================

if submitted:

    if budget <= 0:
        st.error("Please enter a budget greater than ₹0.")

    else:
        recommendations = []

        for cake in cakes:

            score = 0

            # Flavour preference
            if flavour == "Any Flavour":
                score += 1
            elif cake["flavour"] == flavour:
                score += 4

            # Colour preference
            if colour == "Any Colour":
                score += 1
            elif cake["colour"] == colour:
                score += 2

            # Shape preference
            if shape == "Any Shape":
                score += 1
            elif cake["shape"] == shape:
                score += 2

            # Design style preference
            if style == "Any Style":
                score += 1
            elif cake["style"] == style:
                score += 2

            estimated_price = round(cake["price"] * weight)

            if estimated_price <= budget:
                recommendations.append({
                    **cake,
                    "score": score,
                    "estimated_price": estimated_price
                })

        # Highest matching scores first
        recommendations.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        st.divider()
        st.header("✨ Your Recommended Cake Designs")

        if not recommendations:

            st.warning(
                "No cake designs fit your budget. "
                "Please increase your budget or change "
                "your preferences."
            )

        else:

            st.write(
                f"Found {len(recommendations)} matching "
                "options within your budget."
            )

            st.info(
                "These recommendations use existing photos. "
                "The website does not generate or edit images."
            )

            columns = st.columns(2)

            for index, cake in enumerate(recommendations[:6]):

                with columns[index % 2]:

                    st.image(
                        cake["image"],
                        use_container_width=True
                    )

                    st.subheader(cake["name"])

                    st.write(
                        f"**Flavour:** {cake['flavour']}"
                    )

                    st.write(
                        f"**Colour:** {cake['colour']}"
                    )

                    st.write(
                        f"**Shape:** {cake['shape']}"
                    )

                    st.write(
                        f"**Design:** {cake['style']}"
                    )

                    st.write(
                        f"**Weight:** {weight:g} kg"
                    )

                    st.markdown(
                        f"<p class='cake-price'>"
                        f"₹{cake['estimated_price']:,}"
                        f"</p>",
                        unsafe_allow_html=True
                    )

                    if message.strip():
                        st.write(
                            f"**Requested cake message:** "
                            f"{message}"
                        )

                    st.caption(
                        "Displayed message is a preview only; "
                        "it is not added to the cake photo."
                    )

                    st.divider()

# ==================================================
# FOOTER
# ==================================================

st.markdown(
    f"<div class='footer'>{PROJECT_TITLE}</div>",
    unsafe_allow_html=True
)
