# pyrefly: ignore [missing-import]
import streamlit as st
from markitdown import MarkItDown
import os
import tempfile
from pathlib import Path

# Web App ရဲ့ ခေါင်းစဉ်
st.set_page_config(page_title="My MarkItDown Web App")
st.title("📄 File to Markdown Converter")
st.write("Word, Excel, PowerPoint, PDF နဲ့ CSV file တွေကို Markdown အဖြစ် ပြောင်းလဲပေးမယ့် Web App ဖြစ်ပါတယ်။")

# File Upload လုပ်ရန် နေရာဖန်တီးခြင်း
uploaded_file = st.file_uploader("ပြောင်းလဲလိုသော File ကို ရွေးချယ်ပါ", type=["pdf", "docx", "xlsx", "pptx", "html", "csv"])

if uploaded_file is not None:
    st.success(f"'{uploaded_file.name}' ကို အောင်မြင်စွာ Upload လုပ်ပြီးပါပြီ။")
    
    # Convert Button နှိပ်သောအခါ
    if st.button("Convert လုပ်မည်"):
        temp_file_path = None
        with st.spinner('ပြောင်းလဲနေပါသည်... ခေတ္တစောင့်ပါ။'):
            try:
                suffix = Path(uploaded_file.name).suffix
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                    temp_file.write(uploaded_file.getbuffer())
                    temp_file_path = temp_file.name

                # MarkItDown ဖြင့် ပြောင်းလဲခြင်း
                md = MarkItDown()
                result = md.convert(temp_file_path)
                
                # ရလဒ်ကို Web ပေါ်တွင် ပြသခြင်း
                st.subheader("Markdown ရလဒ်:")
                st.text_area("Result", result.text_content, height=300)
                
                # Download ချနိုင်ရန် Button ထည့်ခြင်း
                st.download_button(
                    label="📥 Markdown File ကို Download ဆွဲမည်",
                    data=result.text_content,
                    file_name=f"{uploaded_file.name}.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"Error ဖြစ်နေပါသည်: {e}")
            
            finally:
                # ယာယီသိမ်းထားသော file ကို ပြန်ဖျက်ခြင်း
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
