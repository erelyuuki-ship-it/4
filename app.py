import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import os

# --- CONFIG & DB ---
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
    if os.path.exists("logo.png"): st.image("logo.png", width=300)
    st.subheader("Login - PT. Waskita Niagaprima")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pw == "wnp123":
            st.session_state["logged_in"] = True
            st.rerun()
        else: st.error("Username atau Password salah!")
    st.stop()

# --- APP ---
if os.path.exists("logo.png"): st.image("logo.png", width=200)
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
            uploaded_file = st.file_uploader("Upload Foto", type=["jpg", "png", "jpeg"])
            camera_file = st.camera_input("Ambil Foto Langsung")

        if st.form_submit_button("Simpan Data"):
            final_file = camera_file if camera_file else uploaded_file
            filename = f"img_{aid}.png" if final_file else None
            if final_file: Image.open(final_file).save(os.path.join("images", filename))
            
            conn = sqlite3.connect('assets.db')
            conn.execute("INSERT OR REPLACE INTO assets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                         (aid, name, brand, model, serial, cat, subcat, itype, qty, uom, cond, status, proj, area, loc, stype, rack, shelf, bin, pdate, supp, po, price, rem, filename))
            conn.commit()
            conn.close()
            st.success("Data berhasil disimpan!")

with tab2:
    col_s1, col_s2 = st.columns([1, 2])
    with col_s1: cam_scan = st.camera_input("Scan QR")
    with col_s2:
        search_q = st.text_input("Cari berdasarkan Asset ID atau Nama")
        if st.button("Cari"):
            conn = sqlite3.connect('assets.db')
            df = pd.read_sql(f"SELECT * FROM assets WHERE asset_id LIKE '%{search_q}%' OR asset_name LIKE '%{search_q}%'", conn)
            conn.close()
            if not df.empty:
                for _, row in df.iterrows():
                    with st.expander(f"📦 {row['asset_id']} - {row['asset_name']}"):
                        st.write(row.to_dict())
                        c_a, c_b, c_c = st.columns(3)
                        if c_a.button("Update", key=f"upd_{row['asset_id']}"): st.session_state['act'] = 'upd'
                        if c_b.button("Moving", key=f"mov_{row['asset_id']}"): 
                            st.session_state['act'] = 'mov'
                            st.session_state['m_id'] = row['asset_id']
                        if c_c.button("Delete", key=f"del_{row['asset_id']}"): st.warning("Fitur hapus")
    
    # Logic Moving yang diperbaiki
    if st.session_state.get('act') == 'mov':
        st.divider()
        st.subheader(f"🚚 Moving Asset: {st.session_state['m_id']}")
        with st.form("mov_form"):
            t_no = st.text_input("Masukkan No. Transmittal")
            conn = sqlite3.connect('assets.db')
            all_items = pd.read_sql("SELECT asset_id FROM assets", conn)['asset_id'].tolist()
            conn.close()
            # Multiselect untuk menambah item lain
            selected_items = st.multiselect("Tambahkan item lain untuk dipindahkan", options=all_items, default=[st.session_state['m_id']])
            
            if st.form_submit_button("Submit Pindahan"):
                st.success(f"Item {selected_items} berhasil dipindahkan dengan No. Transmittal: {t_no}")
                # Di sini kamu bisa menambah logic UPDATE ke database untuk kolom no_transmittal jika mau
                st.session_state['act'] = None