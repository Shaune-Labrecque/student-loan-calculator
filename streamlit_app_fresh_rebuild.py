
import streamlit as st

# Alberta branding banner
st.markdown(
    '''
    <div style='background-color:#003366; padding: 15px 20px; color: white; font-family: Helvetica, sans-serif;'>
        <h1 style='margin: 0; font-size: 1.8rem;'>Alberta Student Aid: Loan & Grant Estimator</h1>
    </div>
    ''',
    unsafe_allow_html=True
)

# Initialize session state for tracking form and step
if "step" not in st.session_state:
    st.session_state.step = 0
if "form" not in st.session_state:
    st.session_state.form = {
        "tuition": 0,
        "income": 0,
        "dependent": False,
        "disability": False,
        "disability_amount": 0
    }

f = st.session_state.form

def format_currency(amount):
    return f"${amount:,.2f}"

def calculate_funding(form):
    tuition = form["tuition"]
    income = form["income"]
    dependent = form["dependent"]
    disability = form["disability"]
    disability_amount = form["disability_amount"]

    cg = 2000 if income < 60000 else 0
    ag = 1500 if tuition > 5000 else 0
    dg = 1000 if dependent else 0
    cdg = 2000 if disability else 0
    edg = disability_amount if disability else 0
    adg = 1500 if disability else 0

    cl = 5000
    al = 4000

    total = cg + ag + dg + cdg + edg + adg + cl + al

    return {
        "Canada Grant": cg,
        "Alberta Grant": ag,
        "Dependent Grant": dg,
        "Canada Disability Grant": cdg,
        "Equipment Grant": edg,
        "Alberta Disability Grant": adg,
        "Canada Loan": cl,
        "Alberta Loan": al,
        "Total Funding": total
    }

# UI Flow
if st.session_state.step == 0:
    st.header("Step 1: Enter Basic Info")
    f["tuition"] = st.number_input("Tuition & Fees", min_value=0.0, value=f["tuition"])
    f["income"] = st.number_input("Family Income", min_value=0.0, value=f["income"])
    if st.button("Next"):
        st.session_state.step = 1

elif st.session_state.step == 1:
    st.header("Step 2: Eligibility Details")
    f["dependent"] = st.radio("Are you a dependent student?", ["No", "Yes"]) == "Yes"
    f["disability"] = st.radio("Do you have a permanent disability?", ["No", "Yes"]) == "Yes"

    if f["disability"]:
        f["disability_amount"] = st.number_input("How much do you need for equipment/support?", min_value=0.0, value=f["disability_amount"])

    if st.button("Estimate My Funding"):
        st.session_state.step = 2

elif st.session_state.step == 2:
    st.header("Your Estimated Funding Summary")
    result = calculate_funding(f)

    st.subheader("Grants")
    for k in ["Canada Grant", "Alberta Grant", "Dependent Grant", "Canada Disability Grant", "Equipment Grant", "Alberta Disability Grant"]:
        if result[k] > 0:
            st.markdown(f"✔️ **{k}**: {format_currency(result[k])}")

    st.subheader("Loans")
    st.markdown(f"✔️ **Canada Loan**: {format_currency(result['Canada Loan'])}")
    st.markdown(f"✔️ **Alberta Loan**: {format_currency(result['Alberta Loan'])}")

    st.markdown("---")
    st.markdown(f"🎯 **Total Funding**: {format_currency(result['Total Funding'])}", unsafe_allow_html=True)

    if st.button("🔄 Start Over"):
        for key in st.session_state.form:
            st.session_state.form[key] = 0 if isinstance(st.session_state.form[key], (int, float)) else False
        st.session_state.step = 0
        st.experimental_rerun()
