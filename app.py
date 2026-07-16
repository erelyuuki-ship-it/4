import streamlit as st
import sqlite3
import pandas as pd
import qrcode
from PIL import Image
import os
import io

# --- CONFIG ---
st.set_page_config(page_title="Waskita Asset Management", layout="wide")
os.makedirs("images", exist_ok=True)

def init_db():
    conn = sqlite3.connect('assets.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS assets (
                    asset_id TEXT PRIMARY KEY, asset_name TEXT, brand TEXT, model_type TEXT, 
                    serial_number TEXT, category TEXT, sub_category TEXT, item_type TEXT, 
                    qty TEXT, uom TEXT, condition TEXT, current_status TEXT, 
                    current_project TEXT, current_area TEXT, current_location TEXT, 
                    storage_type TEXT, cabinet_rack TEXT, shelf TEXT, bin TEXT, 
                    purchase_date TEXT, supplier TEXT, po_number TEXT, purchase_price TEXT, 
                    remark TEXT, image_filename TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- LOGIN ---
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if not st.session_state["logged_in"]:
    st.subheader("Login - PT. Waskita Niagaprima")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pw == "wnp123":
            st.session_state["logged_in"] = True
            st.rerun()
        else: st.error("Username atau Password salah!")
    st.stop()

# --- MAIN APP ---
st.title("Asset Management Pro")
tab1, tab2 = st.tabs(["➕ Input & Upload Asset", "📷 Scan & Search"])

with tab1:
    with st.form("input_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            aid = st.text_input("Asset ID")
            name = st.text_input("Asset Name")
            brand = st.text_input("Brand")
            model = st.text_input("Model/Type")
            serial = st.text_input("Serial Number")
            cat = st.selectbox("Category", ["Electrical Tools", "Mechanical Tools", "Hand Tools", "Measuring & Test Instruments", "Lifting Equipment", "Welding Equipment", "Power Equipment", "Personal Protective Equipment", "Vehicle", "Office Equipment", "IT Equipment", "Furniture", "Warehouse Equipment", "Civil Equipment", "Safety Equipment", "Consumable", "Spare Part"])
            subcat = st.text_input("Sub Category")
            itype = st.selectbox("Item Type", ["Individual", "Group", "Tool set", "Consumable"])
            qty = st.text_input("Qty")
            uom = st.text_input("UOM")
            cond = st.text_input("Condition")
            status = st.text_input("Current Status")
        with c2:
            proj = st.text_input("Current Project")
            area = st.text_input("Current Area")
            loc = st.text_input("Current Location")
            stype = st.selectbox("Storage Type", ["Warehouse", "Container", "Tool Box", "Cabinet", "Rack", "Shelf", "Bin", "Vehicle", "Office", "Site", "Workshop", "Consigned", "Personal Issue"])
            rack = st.text_input("Cabinet/Rack")
            shelf = st.text_input("Shelf")
            bin = st.text_input("Bin")
            pdate = st.date_input("Purchase Date").strftime("%Y-%m-%d")
            supp = st.text_input("Supplier")
            po = st.text_input("PO Number")
            price = st.text_input("Purchase Price")
            rem = st.text_area("Remark")
            uploaded_file = st.file_uploader("Upload Foto", type=["jpg", "png", "jpeg"])

        submit = st.form_submit_button("Simpan Data")
        
    # --- LOGIKA DI LUAR FORM ---
    if submit:
        filename = f"img_{aid}.png" if uploaded_file else None
        if uploaded_file: Image.open(uploaded_file).save(os.path.join("images", filename))
        
        conn = sqlite3.connect('assets.db')
        conn.execute("INSERT OR REPLACE INTO assets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                     (aid, name, brand, model, serial, cat, subcat, itype, qty, uom, cond, status, proj, area, loc, stype, rack, shelf, bin, pdate, supp, po, price, rem, filename))
        conn.commit()
        conn.close()
        st.success(f"Data {aid} tersimpan!")
        
        # Simpan state untuk QR
        st.session_state['last_aid'] = aid
        st.rerun()

    # Tampilkan QR jika data baru saja disubmit
    if 'last_aid' in st.session_state:
        qr = qrcode.make(st.session_state['last_aid'])
        buf = io.BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf, width=150)
        st.download_button("Print/Download QR", data=buf.getvalue(), file_name=f"QR_{st.session_state['last_aid']}.png", mime="image/png")
        if st.button("Selesai (Reset QR)"):
            del st.session_state['last_aid']
            st.rerun()

with tab2:
    search_q = st.text_input("Cari Asset ID / Nama")
    if st.button("Cari"):
        conn = sqlite3.connect('assets.db')
        df = pd.read_sql(f"SELECT * FROM assets WHERE asset_id LIKE '%{search_q}%' OR asset_name LIKE '%{search_q}%'", conn)
        conn.close()
        for _, row in df.iterrows():
            with st.expander(f"{row['asset_id']} - {row['asset_name']}"):
                st.write(row.to_dict())