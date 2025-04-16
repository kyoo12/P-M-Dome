import pandas as pd
import streamlit as st
import re
import io
import altair as alt

st.set_page_config(page_title="Swiss Export Compliance Checker", layout="wide")
st.image("Group 51.png", width=100)
st.title("🚧 Swiss Export Control Audit Tool")

# Dual-use and risk keywords (Annex 2)
dual_use_keywords = [
    "CNC", "lathe", "milling", "mill", "punch", "grinder", "laser", "plasma",
    "press", "cutting", "boring", "machining", "drill", "turning", "saw", "shear",
    "EDM", "wire", "robot", "automation", "deburring", "forming", "welding",
    "5-axis", "multi-axis", "linear encoder", "servo", "positioning", "gear", "ball screw",
    "siemens 840d", "heidenhain", "fanuc", "mastercam", "CAD", "CAM", "encryption",
    "military", "missile", "aerospace", "defense", "superalloy", "impeller"
]

# Placeholder keywords for other annexes (extendable)
annex_keywords = {
    "Annex 1 (War Material)": ["rifle", "ammunition", "weapon", "grenade", "missile", "armor"],
    "Annex 3 (Technology/Software)": ["control software", "CAD", "encryption"],
    "Annex 4 (Transit Controlled)": ["transit", "pass-through"],
    "Annex 5 (Restricted Countries)": ["iran", "north korea", "sudan", "syria", "russia"],
    "Annex 6 (Catch-All)": ["nuclear", "uranium", "centrifuge", "bioweapon"],
    "Annex 7 (Sanctions)": ["embargo", "sanctioned"]
}

st.sidebar.subheader("Select Annexes to Apply")
selected_annexes = st.sidebar.multiselect("Annexes", list(annex_keywords.keys()) + ["Annex 2 (Dual-Use)"])

# Extract specs
def extract_specs(text):
    text = str(text).lower()
    axis_match = re.search(r"(\d+)[ -]?axis", text)
    force_match = re.search(r"(\d+)[ -]?tons?", text)
    power_match = re.search(r"(\d+(\.\d+)?)[ ]?kw", text)

    axis_count = int(axis_match.group(1)) if axis_match else None
    force_tons = int(force_match.group(1)) if force_match else None
    power_kw = float(power_match.group(1)) if power_match else None

    return pd.Series({"axis_count": axis_count, "force_tons": force_tons, "power_kw": power_kw})

# Assign risk flags with explanation
def flag_risk(row):
    reasons = []
    text = row["combined_text"]
    axis_count = row["axis_count"]
    force_tons = row["force_tons"]

    if axis_count and axis_count > 5:
        reasons.append("More than 5 axes")
    if force_tons and force_tons >= 200:
        reasons.append("High tonnage (≥ 200 tons)")

    high_risk_terms = [
        ("siemens 840d", "High-end controller: Siemens 840D"),
        ("heidenhain", "High-end controller: Heidenhain"),
        ("fanuc", "High-end controller: Fanuc"),
        ("mastercam", "CAM software: Mastercam"),
        ("5-axis simultaneous", "Simultaneous 5-axis control"),
        ("linear encoder", "Precision motion system: linear encoder"),
        ("servo", "Precision servo system"),
        ("sub-micron", "High precision < 5 microns"),
        ("aerospace", "Aerospace keyword"),
        ("defense", "Defense keyword"),
        ("impeller", "Military-use geometry: impeller"),
        ("superalloy", "Material: superalloy")
    ]
    for keyword, reason in high_risk_terms:
        if keyword in text:
            reasons.append(reason)

    for annex, keywords in annex_keywords.items():
        if annex in row:
            for kw in keywords:
                if kw.lower() in text:
                    reasons.append(f"{annex} keyword: {kw}")

    if "Annex 2 (Dual-Use)" in selected_annexes:
        for kw in dual_use_keywords:
            if kw.lower() in text:
                reasons.append(f"Annex 2 keyword: {kw}")

    if any("Annex" in r or "High-end controller" in r or "High tonnage" in r or "More than 5 axes" in r for r in reasons):
        flag = "❗ High Risk"
    elif reasons:
        flag = "⚠️ Medium Risk"
    else:
        flag = "✅ Safe"

    return pd.Series([flag, ", ".join(sorted(set(reasons))) if reasons else "None"])

# Upload inventory
uploaded_file = st.file_uploader("Upload your inventory CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")

    df = df.rename(columns={
        'ï»¿Lotnumber': 'number',
        'Title': 'title_en',
        'Type': 'attribute-type',
        'Description': 'description_en'
    })

    df["combined_text"] = (
        df["title_en"].astype(str) + " " +
        df["attribute-type"].astype(str) + " " +
        df["description_en"].astype(str)
    ).str.lower()

    for annex, keywords in annex_keywords.items():
        if annex in selected_annexes:
            df[annex] = df["combined_text"].apply(lambda text: any(k in text for k in keywords))

    if "Annex 2 (Dual-Use)" in selected_annexes:
        df["Annex 2 (Dual-Use)"] = df["combined_text"].apply(lambda text: any(k in text for k in dual_use_keywords))

    specs_df = df["description_en"].apply(extract_specs)
    df = pd.concat([df, specs_df], axis=1)

    df[["risk_flag", "risk_reason"]] = df.apply(flag_risk, axis=1)

    st.subheader("🔎 Inventory Scan Results")
    st.dataframe(df[["number", "title_en", "axis_count", "force_tons", "power_kw", "risk_flag", "risk_reason"]])

    st.subheader("📊 Risk Summary Dashboard")
    col1, col2 = st.columns([2, 1])
    with col1:
        summary = df["risk_flag"].value_counts().reset_index()
        summary.columns = ["Risk Level", "Count"]
        chart = alt.Chart(summary).mark_bar(size=40).encode(
            x=alt.X("Risk Level", sort="-y"),
            y="Count",
            color=alt.Color("Risk Level", legend=None),
            tooltip=["Risk Level", "Count"]
        ).properties(width=700, height=400)
        st.altair_chart(chart, use_container_width=True)

    with col2:
        total = len(df)
        flagged = len(df[df["risk_flag"] != "✅ Safe"])
        st.metric("Total Lots", total)
        st.metric("Flagged Lots", flagged)
        st.metric("% Flagged", f"{(flagged / total) * 100:.1f}%")

    # Generate SECO Excel
    if st.button("📤 Generate SECO Risk Summary File"):
        seco_df = df[[
            "number", "title_en", "description_en", "risk_flag", "risk_reason"
        ]].rename(columns={
            "number": "Lot Number",
            "title_en": "Title",
            "description_en": "Description",
            "risk_flag": "Risk Flag",
            "risk_reason": "Risk Reason"
        })

        # Add extra placeholder columns
        for col in ["Estimated Value", "Manufacturer / Model", "Year of Manufacture", "Control System", "Intended Buyer", "Intended Destination"]:
            seco_df[col] = ""

        # Sort by risk
        sort_order = {"❗ High Risk": 0, "⚠️ Medium Risk": 1, "✅ Safe": 2}
        seco_df["_sort"] = seco_df["Risk Flag"].map(sort_order)
        seco_df = seco_df.sort_values("_sort").drop(columns="_sort")

        output_seco = io.BytesIO()
        seco_df.to_excel(output_seco, index=False)

        st.download_button("⬇️ Download SECO Summary (Excel)", data=output_seco.getvalue(), file_name="SECO_Risk_Summary.xlsx")
