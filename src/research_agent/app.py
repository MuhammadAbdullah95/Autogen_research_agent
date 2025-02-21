import streamlit as st
import requests
import os
from dotenv import load_dotenv
from research_agent.agents import ResearchAgent
from research_agent.data_loader import DataLoader


load_dotenv()

print("ok")

st.sidebar.title("Select Agent")
agent_option = st.sidebar.radio(
    "Choose an agent:", ["🔍🌐 Research Agent", "❓🤖 Q&A ChatBot"]
)

if agent_option == "🔍🌐 Research Agent":

    st.title("🤖🔍📚 Virtual Research Assistant")

    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        st.error("groq api key is missing. Please add it to your environment variable")
        st.stop()

    agents = ResearchAgent(groq_api_key)

    data_loader = DataLoader()

    query = st.text_input("Enter a research topic:")

    if st.button("Search"):
        with st.spinner("Fetching research papers..."):
            arxiv_papers = data_loader.fetch_arxiv_papers(query)
            #
            # google_scholar_papers = data_loader.fetch_google_scholar_papers(query)
            # +google_scholar_papers
            all_papers = arxiv_papers

            if not all_papers:
                st.error("Failed to fetch papers. Try Again!")
            else:
                processed_papers = []

            for paper in all_papers:
                summary = agents.summarize_paper(paper["summary"])
                adv_dis = agents.analyze_advantages_disadvantages(summary)

                processed_papers.append(
                    {
                        "title": paper["title"],
                        "link": paper["link"],
                        "pdf_link": paper["pdf_link"],
                        "summary": summary,
                        "advantages_disadvantages": adv_dis,
                    }
                )
            st.subheader("Top Research Papers:")
            for i, paper in enumerate(processed_papers, 1):
                st.markdown(f"### {i}. {paper['title']}")
                st.markdown(f"🔗 [Read Paper]({paper['link']})")
                st.markdown(f"### 🔗 [View pdf]({paper['pdf_link']})")
                st.write(f"**Summary:** {paper['summary']}")
                st.write(f"{paper['advantages_disadvantages']}")
                st.markdown("---")

elif agent_option == "❓🤖 Q&A ChatBot":
    # Backend URLs
    BASE_URL = "http://127.0.0.1:8000"
    UPLOAD_URL = f"{BASE_URL}/upload/"
    PROCESS_URL = f"{BASE_URL}/process/"
    QUERY_URL = f"{BASE_URL}/query/"

    st.title("📚 AI-Powered Research Assistant")

    # Upload PDF file
    st.header("1️⃣ Upload a PDF Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file:
        st.write(f"📄 Selected file: **{uploaded_file.name}**")

        if st.button("Upload File 🚀"):
            with st.spinner("Uploading..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                response = requests.post(UPLOAD_URL, files=files)

                if response.status_code == 200:
                    st.success("✅ File uploaded successfully!")
                    st.json(response.json())
                else:
                    st.error("❌ Upload failed")
                    st.json(response.json())

    # Process the document
    st.header("2️⃣ Process the Document")
    if st.button("Process Document 🛠️"):
        with st.spinner("Processing..."):
            filename = {"file_name": uploaded_file.name}
            response = requests.post(PROCESS_URL, json=filename)

            if response.status_code == 200:
                st.success("✅ Document processed successfully!")
                st.json(response.json())
            else:
                st.error("❌ Processing failed")
                st.json(response.json())

    # Query the document
    st.header("3️⃣ Query the Document")
    query = st.text_input("Enter your question")

    if st.button("Search 🔍"):
        if query:
            with st.spinner("Searching..."):
                response = requests.get(QUERY_URL, json={"query": query})
                if response.status_code == 200:
                    st.success("✅ Results found!")
                    response_data = response.json()
                    # st.write("Response JSON:", response_data)  # Debugging line
                    if "result" in response_data:
                        result = response_data["result"]
                        st.write(result)
                    else:
                        st.error("❌ Query failed")
                        st.json(response.json())

                # if response.status_code == 200:
                #     st.success("✅ Results found!")
                #     result = response.json()["result"]
                #     st.write(result)
                # for i, result in enumerate(results):
                #     st.write(f"**Result {i+1}:**")
                #     st.write(result)
                # else:
                #     st.error("❌ Query failed")
                #     st.json(response.json())
        else:
            st.warning("⚠️ Please enter a query.")
