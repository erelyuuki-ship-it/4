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
                # Tombol Delete
                if c3.button("Delete", key=f"del_{row['asset_id']}"):
                    conn = sqlite3.connect('assets.db')
                    conn.execute("DELETE FROM assets WHERE asset_id = ?", (row['asset_id'],))
                    conn.commit()
                    conn.close()
                    st.success(f"Data {row['asset_id']} berhasil dihapus!")
                    st.rerun() # Refresh halaman agar data hilang dari list