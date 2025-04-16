
# 🇨🇭 Swiss Export Compliance Checker (Dome Auctions Edition)

This Streamlit app helps auction managers assess export risks for industrial machinery and prepare classification requests for SECO (Swiss export authority).

---

## 🚀 Features

### 🔎 Inventory Risk Scanner
- Upload a CSV with auction lots
- Automatically detects high-risk items based on:
  - Axis count, tonnage, precision
  - Control systems (e.g. Siemens 840D, Heidenhain)
  - Keywords from SECO Annexes 1–7
  - Common aerospace/military-use indicators

### 🧠 Intelligent Risk Flagging
- ✅ **Safe**: No red flags
- ⚠️ **Medium Risk**: Minor dual-use indicators
- ❗ **High Risk**: Likely SECO-controlled (e.g. 5+ axes, encrypted CNC, etc.)

### 📊 Visual Dashboard
- Risk breakdown bar chart
- Risk totals + percentages
- Data preview table

### 📤 SECO Export File
- One-click button to generate Excel export:
  - Sorted by Risk Flag
  - Includes title, description, risk explanation, placeholders for value/model/etc.

---

## 📄 File Format

Your input CSV should have the following columns:

| Column              | Description                            |
|---------------------|----------------------------------------|
| Lotnumber           | Lot number or ID                       |
| Title               | Name or headline of machine            |
| Type                | Category or sub-type (optional)        |
| Description         | Full machine description               |

All fields will be combined for analysis.

---

## ✅ Example Output (SECO Export)
| Lot Number | Title                 | Description                           | Risk Flag      | Risk Reason                                         |
|------------|-----------------------|---------------------------------------|----------------|-----------------------------------------------------|
| 123        | CNC Machine           | 5-axis, Siemens 840D, titanium parts  | ❗ High Risk    | More than 5 axes, Siemens 840D, titanium            |
| 124        | Workshop Table        | Basic metal frame                     | ✅ Safe         | None                                                |

---

## 🛠 How to Run

1. Install Python 3.10+ and [Streamlit](https://streamlit.io):
   ```bash
   pip install streamlit pandas openpyxl
   ```

2. Run the app:
   ```bash
   streamlit run app.py
   ```

3. Upload your lot list CSV and review the risk flags!

---

## 📧 Contact

Developed for Dome Auctions.  
Questions or requests? Contact the compliance officer or tech team.
