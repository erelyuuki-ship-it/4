import streamlit as st
import sqlite3
import pandas as pd
import qrcode
import io
import os

st.set_page_config(layout="wide")

# --- DATABASE ---
def init_db():
    conn = sqlite3.connect('assets.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS assets (asset_id TEXT PRIMARY KEY, asset_name TEXT, brand TEXT, model_type TEXT, serial_number TEXT, category TEXT, sub_category TEXT, item_type TEXT, qty TEXT, uom TEXT, condition TEXT, current_status TEXT, current_project TEXT, current_area TEXT, current_location TEXT, storage_type TEXT, cabinet_rack TEXT, shelf TEXT, bin TEXT, purchase_date TEXT, supplier TEXT, po_number TEXT, purchase_price TEXT, remark TEXT, image_filename TEXT)''')
    conn.commit(); conn.close()
init_db()

# --- LOGIN & LOGO ---
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if not st.session_state["logged_in"]:
    if os.path.exists("logo.png"): st.image("logo.png", width=250)
    st.subheader("Login - PT. Waskita Niagaprima")
    if st.button("Login"): 
        if st.text_input("Password", type="password") == "wnp123":
            st.session_state["logged_in"] = True; st.rerun()
    st.stop()

# --- MAIN APP ---
if os.path.exists("logo.png"): st.image("logo.png", width=150)
st.title("Asset Management Pro")
tab1, tab2, tab3 = st.tabs(["🏠 List Aset", "📷 Scan & Search", "⚙️ Pengaturan & Excel"])

with tab1:
    col1, col2 = st.columns([0.9, 0.1])
    with col2:
        if st.button("➕"): st.session_state['show_input'] = True
    
    if st.session_state.get('show_input'):
        st.subheader("Input Data")
        with st.form("input_form"):
            aid = st.text_input("Asset ID")
            name = st.text_input("Asset Name")
            pdate = st.date_input("Purchase Date").strftime("%Y-%m-%d")
            # ... (tambahkan sisa 25 kolom kamu di sini) ...
            if st.form_submit_button("Simpan"):
                conn = sqlite3.connect('assets.db')
                conn.execute("INSERT OR REPLACE INTO assets (asset_id, asset_name, purchase_date) VALUES (?,?,?)", (aid, name, pdate))
                conn.commit(); conn.close(); st.session_state['show_input'] = False; st.rerun()
    else:
        conn = sqlite3.connect('assets.db')
        st.dataframe(pd.read_sql("SELECT * FROM assets", conn))
        conn.close()

with tab2:
    st.subheader("Scan & Search")
    st.camera_input("Scan QR Code") # Kamera Scan
    search_q = st.text_input("Cari Asset ID")
    if st.button("Cari"):
        conn = sqlite3.connect('assets.db')
        df = pd.read_sql(f"SELECT * FROM assets WHERE asset_id LIKE '%{search_q}%'", conn)
        for _, row in df.iterrows():
            with st.expander(row['asset_id']):
                # Tampilkan QR
                qr = qrcode.make(row['asset_id'])
                buf = io.BytesIO(); qr.save(buf, format="PNG")
                st.image(buf, width=100)
                if st.button("Delete", key=f"del_{row['asset_id']}"):
                    conn.execute("DELETE FROM assets WHERE asset_id = ?", (row['asset_id'],))
                    conn.commit(); conn.close(); st.rerun()
        conn.close()

with tab3:
    st.subheader("Upload Excel")
    uploaded_file = st.file_uploader("Pilih file Excel", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        conn = sqlite3.connect('assets.db')
        df.to_sql('assets', conn, if_exists='append', index=False)
        conn.close(); st.success("Excel berhasil diunggah!")   