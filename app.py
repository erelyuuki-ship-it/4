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

def show_logo():
    if os.path.exists("logo.png"): st.image("logo.png", width=200)

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

# --- NAVIGATION ---
if "page" not in st.session_state: st.session_state["page"] = "Home"

# --- PAGES ---
if st.session_state["page"] == "Home":
    show_logo()
    st.title("List Asset")
    if st.button("➕ Tambah Aset Baru"):
        st.session_state["page"] = "Input"
        st.rerun()
    
    st.divider()
    conn = sqlite3.connect('assets.db')
    df = pd.read_sql("SELECT * FROM assets", conn)
    conn.close()
    st.dataframe(df)
    
    if st.button("🔍 Lanjut ke Scan & Search"):
        st.session_state["page"] = "Search"
        st.rerun()

elif st.session_state["page"] == "Input":
    st.title("Input Asset Baru")
    with st.form("input_form"):
        # (Form Input tetap sama dengan 25 kolom)
        c1, c2 = st.columns(2)
        with c1:
            aid = st.text_input("Asset ID")
            name = st.text_input("Asset Name")
            # ... (semua kolom input lainnya) ...
        with c2:
            pdate = st.date_input("Purchase Date").strftime("%Y-%m-%d")
            uploaded_file = st.file_uploader("Upload Foto", type=["jpg", "png", "jpeg"])
        
        if st.form_submit_button("Simpan Data"):
            # (Logika simpan tetap sama)
            st.success("Data Tersimpan!")
            if st.button("Kembali ke Home"):
                st.session_state["page"] = "Home"
                st.rerun()

elif st.session_state["page"] == "Search":
    st.title("Scan & Search")
    # (Logika Scan & Search dengan fitur Update, Moving, Delete)
    if st.button("🔙 Kembali ke Home"):
        st.session_state["page"] = "Home"
        st.rerun()