import streamlit as st
import sqlite3
import pandas as pd
import qrcode
from io import BytesIO
import cv2
import numpy as np
from PIL import Image
import os

# --- CONFIG ---
st.set_page_config(page_title="Waskita Asset Management", layout="wide")
os.makedirs("images", exist_ok=True)

# Fungsi untuk menampilkan logo
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
tab1, tab2 = st.tabs(["➕ Input & Upload Asset", "🔍 Scan, Search & Print"])

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
            subcat = st.text_input("Sub Category (Ketik manual)")
            itype = st.selectbox("Item Type", ["Individual", "Group", "Tool Set Consumable"])
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
            
            # Opsi Foto: Kamera atau Upload
            tipe_foto = st.radio("Pilih sumber foto:", ["Upload File", "Ambil Foto (Kamera)"])
            uploaded_file = None
            if tipe_foto == "Upload File":
                uploaded_file = st.file_uploader("Upload Foto", type=["jpg", "png"])
            else:
                uploaded_file = st.camera_input("Ambil foto langsung")

        if st.form_submit_button("Simpan Data"):
            filename = None
            if uploaded_file:
                filename = f"img_{aid}.png"
                Image.open(uploaded_file).save(os.path.join("images", filename))
            
            conn = sqlite3.connect('assets.db')
            conn.execute("INSERT OR REPLACE INTO assets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                         (aid, name, brand, model, serial, cat, subcat, itype, qty, uom, cond, status, proj, area, loc, stype, rack, shelf, bin, pdate, supp, po, price, rem, filename))
            conn.commit()
            conn.close()
            st.success("Data berhasil disimpan!")

with tab2:
    # Fitur scan tetap ada di sini
    st.write("Gunakan fitur Search untuk mencari data.")
    search_q = st.text_input("Cari Asset ID atau Nama")
    if search_q:
        conn = sqlite3.connect('assets.db')
        df = pd.read_sql(f"SELECT * FROM assets WHERE asset_id LIKE '%{search_q}%' OR asset_name LIKE '%{search_q}%'", conn)
        conn.close()
        for _, row in df.iterrows():
            st.write(row.to_dict())