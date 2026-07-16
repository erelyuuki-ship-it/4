import streamlit as st
import sqlite3
import pandas as pd
import qrcode
from PIL import Image
import os
import io

st.set_page_config(layout="wide")

# --- DATABASE ---
def init_db():
    conn = sqlite3.connect('assets.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS assets (asset_id TEXT PRIMARY KEY, asset_name TEXT, brand TEXT, model_type TEXT, serial_number TEXT, category TEXT, sub_category TEXT, item_type TEXT, qty TEXT, uom TEXT, condition TEXT, current_status TEXT, current_project TEXT, current_area TEXT, current_location TEXT, storage_type TEXT, cabinet_rack TEXT, shelf TEXT, bin TEXT, purchase_date TEXT, supplier TEXT, po_number TEXT, purchase_price TEXT, remark TEXT, image_filename TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- LOGIN ---
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if not st.session_state["logged_in"]:
    st.subheader("Login - PT. Waskita Niagaprima")
    if st.button("Login"): st.session_state["logged_in"] = True; st.rerun()
    st.stop()

# --- MAIN APP ---
st.title("Asset Management Pro")
tab1, tab2, tab3 = st.tabs(["🏠 List Aset", "📷 Scan & Search", "⚙️ Pengaturan"])

with tab1:
    col1, col2 = st.columns([0.9, 0.1])
    with col2:
        if st.button("➕"): st.session_state['show_input'] = True
    
    if st.session_state.get('show_input'):
        st.subheader("Input Asset Baru")
        with st.form("input_form"):
            aid = st.text_input("Asset ID")
            name = st.text_input("Asset Name")
            pdate = st.date_input("Purchase Date").strftime("%Y-%m-%d")
            # (Pastikan 25 kolom kamu ada di sini)
            if st.form_submit_button("Simpan"):
                conn = sqlite3.connect('assets.db')
                conn.execute("INSERT OR REPLACE INTO assets (asset_id, asset_name, purchase_date) VALUES (?,?,?)", (aid, name, pdate))
                conn.commit(); conn.close()
                st.session_state['show_input'] = False; st.rerun()
    else:
        conn = sqlite3.connect('assets.db')
        st.dataframe(pd.read_sql("SELECT * FROM assets", conn))
        conn.close()

with tab2:
    search_q = st.text_input("Cari Asset ID atau Nama")
    if st.button("Cari"):
        conn = sqlite3.connect('assets.db')
        df = pd.read_sql(f"SELECT * FROM assets WHERE asset_id LIKE '%{search_q}%' OR asset_name LIKE '%{search_q}%'", conn)
        conn.close()
        for _, row in df.iterrows():
            with st.expander(f"📦 {row['asset_id']} - {row['asset_name']}"):
                st.write(row.to_dict())
                c1, c2, c3 = st.columns(3)
                if c3.button("Delete", key=f"del_{row['asset_id']}"):
                    conn = sqlite3.connect('assets.db')
                    conn.execute("DELETE FROM assets WHERE asset_id = ?", (row['asset_id'],))
                    conn.commit(); conn.close()
                    st.rerun()

with tab3:
    st.write("Pengaturan")