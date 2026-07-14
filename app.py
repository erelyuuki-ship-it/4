import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import os

# --- CONFIG ---
st.set_page_config(page_title="Waskita Asset Management", layout="wide")
os.makedirs("images", exist_ok=True)

def show_logo():
    if os.path.exists("logo.png"):
        st.image("logo.png", width=300)

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
    show_logo()
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
show_logo()
st.subheader("Asset Management Pro")
tab1, tab2 = st.tabs(["➕ Input & Upload Asset", "📷 Scan & Search"])

with tab1:
    with st.form("input_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            aid = st.text_input("Asset ID")
            name = st.text_input("Asset Name")
            brand = st.text_input("Brand")
            model = st.text_input("Model/Type")
            serial = st.text_input("Serial Number")
            cat = st.selectbox("Category", ["Electrical Tools", "Mechanical Tools", "Hand Tools", "Measuring & Test Instruments", "Lifting Equipment", "Welding Equipment", "Power Equipment", "Personal Protective Equipment", "Vehicle", "Office Equipment", "IT Equipment", "Furniture", "Warehouse Equipment", "Civil Equipment", "Safety Equipment", "Consumable", "Spare Part"])
            subcat = st.text_input("Sub Category")
            # Item Type sudah dipisah
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
            pdate = st.text_input("Purchase Date")
            supp = st.text_input("Supplier")
            po = st.text_input("PO Number")
            price = st.text_input("Purchase Price")
            rem = st.text_area("Remark")
            
            # Pilihan Foto
            opsi_foto = st.radio("Metode Foto:", ["Upload File", "Ambil Foto Langsung"])
            if opsi_foto == "Upload File":
                uploaded_file = st.file_uploader("Pilih Foto", type=["jpg", "png", "jpeg"])
            else:
                uploaded_file = st.camera_input("Ambil Foto Kamera")

        if st.form_submit_button("Simpan Data"):
            filename = None
            if uploaded_file:
                filename = f"img_{aid}.png"
                Image.open(uploaded_file).save(os.path.join("images", filename))
            
            conn = sqlite3.connect('assets.db')
            try:
                conn.execute("INSERT OR REPLACE INTO assets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                             (aid, name, brand, model, serial, cat, subcat, itype, qty, uom, cond, status, proj, area, loc, stype, rack, shelf, bin, pdate, supp, po, price, rem, filename))
                conn.commit()
                st.success("Data berhasil disimpan!")
            except Exception as e:
                st.error(f"Error Database: {e}")
            conn.close()

with tab2:
    st.subheader("📷 Scan QR Code")
    cam_img = st.camera_input("Arahkan Kamera ke QR Code")
    st.divider()
    st.subheader("🔍 Search Data")
    search_q = st.text_input("Cari Asset ID atau Nama")
    if search_q:
        conn = sqlite3.connect('assets.db')
        df = pd.read_sql(f"SELECT * FROM assets WHERE asset_id LIKE '%{search_q}%' OR asset_name LIKE '%{search_q}%'", conn)
        conn.close()
        if not df.empty:
            for _, row in df.iterrows():
                st.write(row.to_dict())
        else:
            st.warning("Data tidak ditemukan.")