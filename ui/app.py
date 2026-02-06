import streamlit as st
from ingestion.pdf_loader import PDFLoader
from rag_engine.vector_store import RAGEngine
from metadata_extractor.extractor import MetadataExtractor
from chat_engine.core import ChatEngine
from config.settings import settings
import os

st.set_page_config(page_title="Jules AI - Contract Chatbot", layout="wide")

# Initialize Session State
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = RAGEngine()

if "metadata_list" not in st.session_state:
    st.session_state.metadata_list = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = ChatEngine(st.session_state.rag_engine)

if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

st.title("📄 AI Contract Chatbot")
st.markdown("Upload your contract PDFs and ask questions about them. No data is stored persistently.")

# Sidebar for Uploads
with st.sidebar:
    st.header("Upload Contracts")
    uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

    if st.button("Process Contracts"):
        if uploaded_files:
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, uploaded_file in enumerate(uploaded_files):
                if uploaded_file.name in st.session_state.processed_files:
                    continue

                status_text.text(f"Processing {uploaded_file.name}...")

                # Ingest
                try:
                    text = PDFLoader.extract_text_from_stream(uploaded_file, uploaded_file.name)

                    if text:
                        # Index
                        st.session_state.rag_engine.index_documents(text, uploaded_file.name)

                        # Extract Metadata
                        try:
                            extractor = MetadataExtractor()
                            meta = extractor.extract(text)
                        except Exception:
                            meta = None

                        st.session_state.metadata_list.append({
                            "filename": uploaded_file.name,
                            "metadata": meta
                        })
                        st.session_state.processed_files.add(uploaded_file.name)
                    else:
                        st.error(f"Could not extract text from {uploaded_file.name}")
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {e}")

                progress_bar.progress((i + 1) / len(uploaded_files))

            status_text.text("Processing Complete!")
            st.success("Contracts processed successfully.")

    st.divider()
    st.header("Processed Contracts")
    if not st.session_state.metadata_list:
        st.info("No contracts processed yet.")

    for item in st.session_state.metadata_list:
        with st.expander(item["filename"]):
            meta = item["metadata"]
            if meta:
                st.write(f"**Title:** {meta.title or 'N/A'}")
                st.write(f"**Vendor:** {meta.vendor or 'N/A'}")
                st.write(f"**Client:** {meta.client or 'N/A'}")
                st.write(f"**Start:** {meta.start_date or 'N/A'}")
                st.write(f"**End:** {meta.end_date or 'N/A'}")
            else:
                st.write("Metadata extraction failed or unavailable.")

# Chat Interface
st.subheader("Chat with your Contracts")

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask a question (e.g., 'When does the vendor contract expire?')..."):
    # User message
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant message
    with st.chat_message("assistant"):
        with st.spinner("Analyzing contracts..."):
            response = st.session_state.chat_engine.process_query(prompt)
            answer = response["answer"]
            st.markdown(answer)

            # Show sources in expander
            if response.get("source_documents"):
                with st.expander("View Source Context"):
                    for i, doc in enumerate(response["source_documents"]):
                        st.markdown(f"**Source {i+1}: {doc.metadata.get('source')}**")
                        st.caption(doc.page_content)

    st.session_state.chat_history.append({"role": "assistant", "content": answer})
