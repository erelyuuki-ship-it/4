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

def show_logo():
    if os.path.exists("logo.png"):
        st.image("logo.png", width=400)
    else:
        st.error("File 'logo.png' tidak ditemukan!")

def init_db():
    conn = sqlite3.connect('assets.db')
    c = conn.cursor()
    # Menggunakan TEXT untuk semua kolom agar fleksibel
    c.execute('''CREATE TABLE IF NOT EXISTS assets (
                    asset_id TEXT PRIMARY KEY, asset_name TEXT, bin TEXT, brand TEXT, 
                    cabinet_rack TEXT, category TEXT, condition TEXT, current_area TEXT, 
                    current_location TEXT, current_pic TEXT, current_project TEXT, 
                    current_status TEXT, item_type TEXT, last_movement TEXT, 
                    last_update TEXT, model_type TEXT, no_transmittal TEXT, 
                    po_number TEXT, purchase_date TEXT, purchase_price TEXT, 
                    qr_code TEXT, qty TEXT, remark TEXT, serial_number TEXT, 
                    shelf TEXT, storage_type TEXT, sub_category TEXT, 
                    supplier TEXT, uom TEXT, image_filename TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- LOGIN ---
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if not st.session_state["logged_in"]:
    show_logo()
    st.subheader("Login Asset Management")
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
st.subheader("Asset Management Pro - PT. Waskita Niagaprima")
tab1, tab2 = st.tabs(["➕ Input & Upload Asset", "🔍 Scan, Search & Print"])

with tab1:
    with st.form("input_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            aid = st.text_input("Asset ID")
            name = st.text_input("Asset Name")
            bin = st.text_input("Bin")
            brand = st.text_input("Brand")
            rack = st.text_input("Cabinet/Rack")
        with c2:
            cat = st.text_input("Category")
            cond = st.text_input("Condition")
            c_area = st.text_input("Current Area")
            c_loc = st.text_input("Current Location")
            pic = st.text_input("Current PIC")
        with c3:
            proj = st.text_input("Current Project")
            stat = st.text_input("Current Status")
            itype = st.text_input("Item Type")
            move = st.text_input("Last Movement")
            upd = st.text_input("Last Update")
        
        c4, c5, c6 = st.columns(3)
        with c4:
            model = st.text_input("Model/Type")
            trans = st.text_input("No. Transmittal")
            po = st.text_input("PO Number")
            pdate = st.text_input("Purchase Date")
            price = st.text_input("Purchase Price") # Sudah jadi text input
        with c5:
            qr = st.text_input("QR Code")
            qty = st.text_input("Qty") # Sudah jadi text input
            rem = st.text_area("Remark")
            serial = st.text_input("Serial Number")
            shelf = st.text_input("Shelf")
        with c6:
            stype = st.text_input("Storage Type")
            subcat = st.text_input("Sub Category")
            supp = st.text_input("Supplier")
            uom = st.text_input("UOM")
            uploaded_file = st.file_uploader("Upload Foto Barang", type=["jpg", "png", "jpeg"])
            
        if st.form_submit_button("Simpan Data"):
            filename = None
            if uploaded_file:
                filename = f"img_{aid}.png"
                Image.open(uploaded_file).save(os.path.join("images", filename))
            
            conn = sqlite3.connect('assets.db')
            try:
                conn.execute("INSERT INTO assets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                             (aid, name, bin, brand, rack, cat, cond, c_area, c_loc, pic, proj, stat, itype, move, upd, model, trans, po, pdate, price, qr, qty, rem, serial, shelf, stype, subcat, supp, uom, filename))
                conn.commit()
                st.success("Data berhasil disimpan!")
            except Exception as e: st.error(f"Error: {e}")
            conn.close()

with tab2:
    img = st.camera_input("Scan QR Code")
    if img:
        bytes_data = img.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        found_id = cv2.QRCodeDetector().detectAndDecode(cv2_img)[0]
        if found_id: st.success(f"Ditemukan: {found_id}")
    
    search_q = st.text_input("Cari Asset ID atau Nama:")
    if search_q:
        conn = sqlite3.connect('assets.db')
        df = pd.read_sql(f"SELECT * FROM assets WHERE asset_id LIKE '%{search_q}%' OR asset_name LIKE '%{search_q}%'", conn)
        conn.close()
        if not df.empty:
            for _, row in df.iterrows():
                with st.expander(f"📦 {row['asset_id']} - {row['asset_name']}"):
                    st.write(row.to_dict())
        else: st.warning("Data tidak ditemukan.")