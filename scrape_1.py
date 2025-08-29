# import streamlit as st
# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
#
# st.title("Link Detective Domain Info 🕵️‍♂️")
#
# # ---- User input ----
# domain_input = st.text_input("Enter domain(s) (comma separated if multiple):")
#
# if st.button("Fetch Data") and domain_input:
#     domains_list = [d.strip() for d in domain_input.split(",")]
#     st.write("📌 Domains loaded:", domains_list)
#
#     # ---- Start session ----
#     session = requests.Session()
#     home = session.get("https://linkdetective.pro/")
#     soup = BeautifulSoup(home.text, "html.parser")
#
#     csrf_token = None
#     token_input = soup.find("input", {"name": "_token"})
#     if token_input:
#         csrf_token = token_input["value"]
#
#     if not csrf_token:
#         csrf_token = session.cookies.get("XSRF-TOKEN")
#
#     st.success(f"✅ CSRF token fetched: {csrf_token}")
#
#     # ---- Prepare results list ----
#     results = []
#
#     # ---- Process each domain ----
#     for domain_name in domains_list:
#         payload = {
#             "draw": 5,
#             "start": 0,
#             "length": 50,
#             "_token": csrf_token,
#             "domains[]": domain_name,
#             "buttons": "true"
#         }
#
#         resp = session.post("https://linkdetective.pro/api/domains", data=payload)
#
#         try:
#             data = resp.json()
#         except ValueError:
#             st.error(f"❌ Response not JSON for {domain_name}")
#             continue
#
#         sellers_by_domain = data.get("sellers", [])
#         domains = [row.get("Domain") for row in data.get("data", [])]
#
#         if not sellers_by_domain:
#             results.append({
#                 "Domain": domain_name,
#                 "Contact": "(none)",
#                 "Price": "",
#                 "Date": ""
#             })
#         else:
#             for i, sellers in enumerate(sellers_by_domain):
#                 dom = domains[i] if i < len(domains) else domain_name
#                 for s in sellers:
#                     results.append({
#                         "Domain": dom,
#                         "Contact": s.get("contacts"),
#                         "Price": s.get("price"),
#                         "Date": s.get("date")
#                     })
#
#     # ---- Show results in table ----
#     if results:
#         df = pd.DataFrame(results)
#         st.dataframe(df)
#     else:
#         st.info("No data found for the provided domain(s).")


import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.title("Link Detective Domain Info 🕵️‍♂️")

# ---- User input ----
domain_input = st.text_input("Enter domain(s) (comma separated if multiple):")

def get_csrf_token(session):
    """Fetch a fresh CSRF token from the homepage."""
    home = session.get("https://linkdetective.pro/")
    soup = BeautifulSoup(home.text, "html.parser")
    token_input = soup.find("input", {"name": "_token"})
    if token_input:
        return token_input["value"]
    return session.cookies.get("XSRF-TOKEN")

def fetch_domain_data(session, csrf_token, domain_name):
    """Fetch domain data, retrying if CSRF token fails."""
    payload = {
        "draw": 5,
        "start": 0,
        "length": 50,
        "_token": csrf_token,
        "domains[]": domain_name,
        "buttons": "true"
    }

    resp = session.post("https://linkdetective.pro/api/domains", data=payload)

    # If token expired or invalid, retry once with new token
    if resp.status_code == 419 or "invalid" in resp.text.lower():
        csrf_token = get_csrf_token(session)
        payload["_token"] = csrf_token
        resp = session.post("https://linkdetective.pro/api/domains", data=payload)

    try:
        return resp.json()
    except ValueError:
        return None

if st.button("Fetch Data") and domain_input:
    domains_list = [d.strip() for d in domain_input.split(",")]
    # st.write("📌 Domains loaded:", domains_list)

    session = requests.Session()
    csrf_token = get_csrf_token(session)
    # st.success(f"✅ CSRF token fetched: {csrf_token}")

    results = []

    for domain_name in domains_list:
        data = fetch_domain_data(session, csrf_token, domain_name)
        if not data:
            st.error(f"❌ Response not JSON or failed for {domain_name}")
            continue

        sellers_by_domain = data.get("sellers", [])
        domains = [row.get("Domain") for row in data.get("data", [])]

        if not sellers_by_domain:
            results.append({
                "Domain": domain_name,
                "Contact": "(none)",
                "Price": "",
                "Date": ""
            })
        else:
            for i, sellers in enumerate(sellers_by_domain):
                dom = domains[i] if i < len(domains) else domain_name
                for s in sellers:
                    results.append({
                        "Domain": dom,
                        "Contact": s.get("contacts"),
                        "Price": s.get("price"),
                        "Date": s.get("date")
                    })

    if results:
        df = pd.DataFrame(results)
        st.dataframe(df)
    else:
        st.info("No data found for the provided domain(s).")
