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
tab1, tab2, tab3 = st.tabs(["🏠 List Aset", "📷 Scan & Search", "⚙️ Pengaturan"])

with tab1:
    # Tombol Tambah di kanan atas
    c_h1, c_h2 = st.columns([0.9, 0.1])
    with c_h2:
        if st.button("➕"): st.session_state['show_input'] = True
    
    if st.session_state.get('show_input'):
        st.subheader("Input Asset Baru")
        with st.form("input_form", clear_on_submit=False):
            c1, c2 = st.columns(2)
            with c1:
                aid = st.text_input("Asset ID")
                name = st.text_input("Asset Name")
                # ... (lanjutkan 25 kolom di sini) ...
                pdate = st.date_input("Purchase Date").strftime("%Y-%m-%d")
            with c2:
                uploaded_file = st.file_uploader("Upload Foto", type=["jpg", "png", "jpeg"])
            
            if st.form_submit_button("Simpan Data"):
                # Simpan logic...
                st.session_state['last_aid'] = aid
                st.rerun()
        if st.button("Batal"): st.session_state['show_input'] = False; st.rerun()
    else:
        conn = sqlite3.connect('assets.db')
        df = pd.read_sql("SELECT * FROM assets", conn)
        conn.close()
        st.dataframe(df)

with tab2:
    col_s1, col_s2 = st.columns([1, 2])
    with col_s1: st.camera_input("Scan QR")
    with col_s2:
        search_q = st.text_input("Cari Asset ID atau Nama")
        if st.button("Cari"):
            # Logic Search...
            pass
    
    # Form Moving dengan multiselect
    # (Logika Update/Moving/Delete)

with tab3:
    st.write("Fitur Tambahan / Pengaturan")