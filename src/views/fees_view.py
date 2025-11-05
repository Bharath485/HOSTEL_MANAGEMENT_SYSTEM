
import streamlit as st
from ..services.fee_service import fees_store

def show_fees():
    st.subheader("Fees (Starter Stub)")
    st.info("This section is scaffolded. Add fees create/list logic here (CSV columns already defined).")
    st.dataframe(fees_store.list_all())
