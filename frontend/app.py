import streamlit as st
import requests

st.set_page_config(page_title="Gov Scheme Finder", layout="centered")

st.title("🏛️ Government Scheme Finder")
st.markdown("Describe your situation to find schemes you qualify for.")

profile_input = st.text_area(
    "Your Profile", 
    placeholder="e.g., I am a 25-year-old female SC student whose family income is 2 lakhs, looking for higher education support."
)

if st.button("Find Schemes", type="primary"):
    if profile_input:
        with st.spinner("Analyzing government databases..."):
            try:
                res = requests.post("http://127.0.0.1:8000/api/schemes", json={"profile": profile_input})
                data = res.json()
                
                if data.get("matches"):
                    st.success(f"Found {len(data['matches'])} matching verified scheme(s)!")
                    for match in data["matches"]:
                        with st.expander(f"🏛️ {match['name']} — {match['status']}", expanded=True):
                            st.markdown(f"**Why you qualify:** {match['reasoning']}")
                            
                            # Create an elegant two-column layout for product-grade delivery
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("### 💰 Benefits Provided")
                                st.write(match.get("benefits", "N/A"))
                                
                                st.markdown("### 📑 Required Documentation")
                                st.write(match.get("documents", "N/A"))
                                
                            with col2:
                                st.markdown("### 🚀 Step-by-Step Application")
                                st.write(match.get("how_to_apply", "N/A"))
                                
                                if match.get("url") and match["url"] != "N/A":
                                    st.markdown(f"[🔗 Open Official Government Portal]({match['url']})")
                            st.markdown("---")
                else:
                    st.warning("No exact matches found for this specific profile in our database.")
            except Exception as e:
                st.error("Error connecting to the backend server. Is FastAPI running?")
    else:
        st.warning("Please enter your details first.")