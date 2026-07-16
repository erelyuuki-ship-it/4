import streamlit as st
import sqlite3
import pandas as pd
import qrcode
import io
import os

st.set_page_config(layout="wide")

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
tab1, tab2, tab3 = st.tabs(["🏠 List Aset", "📷 Scan & Search", "⚙️ Pengaturan"])

with tab1:
    col1, col2 = st.columns([0.9, 0.1])
    with col2:
        if st.button("➕"): st.session_state['show_input'] = True
    
    if st.session_state.get('show_input'):
        with st.form("input_form"):
            st.subheader("Input Asset Baru")
            aid = st.text_input("Asset ID")
            name = st.text_input("Asset Name")
            pdate = st.date_input("Purchase Date").strftime("%Y-%m-%d")
            # ... (tambahkan sisa 25 kolom lainnya) ...
            if st.form_submit_button("Simpan"):
                conn = sqlite3.connect('assets.db')
                conn.execute("INSERT OR REPLACE INTO assets (asset_id, asset_name, purchase_date) VALUES (?,?,?)", (aid, name, pdate))
                conn.commit(); conn.close()
                st.session_state['last_aid'] = aid; st.rerun()
    else:
        conn = sqlite3.connect('assets.db')
        st.dataframe(pd.read_sql("SELECT * FROM assets", conn))
        conn.close()

with tab2:
    search_q = st.text_input("Cari Asset ID/Nama")
    if st.button("Cari"):
        conn = sqlite3.connect('assets.db')
        items = pd.read_sql(f"SELECT * FROM assets WHERE asset_id LIKE '%{search_q}%'", conn)
        for _, row in items.iterrows():
            with st.expander(row['asset_id']):
                c1, c2, c3 = st.columns(3)
                if c1.button("Update", key=f"upd_{row['asset_id']}"): pass
                if c2.button("Moving", key=f"mov_{row['asset_id']}"): pass
                if c3.button("Delete", key=f"del_{row['asset_id']}"):
                    conn.execute("DELETE FROM assets WHERE asset_id = ?", (row['asset_id'],))
                    conn.commit(); st.rerun()
        conn.close()

with tab3:
    st.write("Pengaturan")