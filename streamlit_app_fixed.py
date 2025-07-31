
import streamlit as st

st.set_page_config(page_title="Student Aid Estimator", page_icon="🎓", layout="centered")

# CSS styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        color: #1f1f1f;
        font-weight: bold;
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .sub-text {
        text-align: center;
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 2rem;
    }
    .result-box {
        background: #ffffff;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 0 10px rgba(0,0,0,0.05);
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 0
if "form" not in st.session_state:
    st.session_state.form = {
        "tuition": 0,
        "living": "",
        "weeks": 34,
        "program_length": "1",
        "income": 0,
        "family_size": 1,
        "independent": False,
        "dependents": 0,
        "disability": False,
        "disability_costs": 0
    }

def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

def format_currency(amount):
    return f"${amount:,.2f}"

def calculate():
    f = st.session_state.form
    living_costs = {"pay-rent": 6920, "dont-pay-rent": 6592}
    tuition = float(f["tuition"])
    living = living_costs.get(f["living"], 0)
    weeks = int(f["weeks"])
    program_length = int(f["program_length"])
    income = float(f["income"])
    dependents = int(f["dependents"])
    disability_costs = float(f["disability_costs"]) if f["disability"] else 0

    books = 1000
    computer = 500
    student_contribution = 1500

    allowable_costs = tuition + books + computer + living
    assessed_need = max(0, allowable_costs - student_contribution)

    canada_loan = min(assessed_need * 0.6, 300 * weeks)
    max_total_loans = 8500 * (weeks / 17)
    alberta_loan = min(max(0, assessed_need - canada_loan), max_total_loans - canada_loan)

    canada_grant = 0
    dependent_grant = 0
    alberta_grant = 0
    canada_disability_grant = 0
    equipment_grant = 0
    alberta_disability_grant = 0

    if program_length >= 2 and income < 53318:
        canada_grant = 121.1538 * weeks
        dependent_grant = 64.6153 * weeks * dependents
    elif program_length == 1:
        alberta_grant = 425 * (weeks / 4)

    if f["disability"]:
        canada_disability_grant = 2800
        equipment_grant = min(disability_costs, 20000)
        alberta_disability_grant = min(max(0, disability_costs - 20000), 3000)

    total_grants = sum([
        canada_grant, dependent_grant, alberta_grant,
        canada_disability_grant, equipment_grant, alberta_disability_grant
    ])
    total_loans = canada_loan + alberta_loan

    return {
        "Canada Loan": canada_loan,
        "Alberta Loan": alberta_loan,
        "Canada Grant": canada_grant,
        "Dependent Grant": dependent_grant,
        "Alberta Grant": alberta_grant,
        "Canada Disability Grant": canada_disability_grant,
        "Equipment Grant": equipment_grant,
        "Alberta Disability Grant": alberta_disability_grant,
        "Total Grants": total_grants,
        "Total Loans": total_loans,
        "Total Funding": total_grants + total_loans
    }

st.markdown("<div class='main-title'>🎓 Student Aid Estimator</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-text'>Answer a few quick questions to estimate your loan and grant funding</div>", unsafe_allow_html=True)

f = st.session_state.form
step = st.session_state.step

steps = [
    "Tuition & Fees",
    "Living Situation",
    "Weeks of Study",
    "Program Length",
    "Family Income",
    "Family Size",
    "Student Status",
    "Dependents",
    "Disability Status"
]

if f["disability"]:
    steps.append("Disability Costs")

st.progress((step + 1) / len(steps))

# Render current step
if steps[step] == "Tuition & Fees":
    f["tuition"] = st.number_input("Enter your total tuition (incl. fees)", min_value=0.0, value=float(f["tuition"]))
elif steps[step] == "Living Situation":
    f["living"] = st.selectbox("Do you pay rent?", ["", "pay-rent", "dont-pay-rent"],
        format_func=lambda x: {"": "Select...", "pay-rent": "Yes", "dont-pay-rent": "No"}.get(x, x))
elif steps[step] == "Weeks of Study":
    f["weeks"] = st.slider("How many weeks will you study?", 1, 52, f["weeks"])
elif steps[step] == "Program Length":
    f["program_length"] = st.selectbox("Length of your program", ["1", "2", "3", "4", "5"], index=int(f["program_length"]) - 1)
elif steps[step] == "Family Income":
    f["income"] = st.number_input("Family income (Line 15000)", min_value=0.0, value=float(f["income"]))
elif steps[step] == "Family Size":
    f["family_size"] = st.slider("How many people in your family?", 1, 12, f["family_size"])
elif steps[step] == "Student Status":
    f["independent"] = st.checkbox("Are you an independent student?", value=f["independent"])
elif steps[step] == "Dependents":
    f["dependents"] = st.number_input("Number of dependent children under 12", min_value=0, value=int(f["dependents"]))
elif steps[step] == "Disability Status":
    f["disability"] = st.checkbox("Do you have a permanent disability?", value=f["disability"])
elif steps[step] == "Disability Costs":
    f["disability_costs"] = st.number_input("Disability-related costs (services/equipment)", min_value=0.0, value=float(f["disability_costs"]))

# Navigation
col1, col2, col3 = st.columns([1, 4, 1])
with col1:
    if step > 0:
        st.button("← Back", on_click=prev_step)
with col3:
    if step < len(steps) - 1:
        st.button("Next →", on_click=next_step)
    else:
        if st.button("🎯 Estimate My Funding"):
            result = calculate()
            st.markdown("<div class='result-box'>", unsafe_allow_html=True)
            st.subheader("Your Estimated Funding")

            st.write("### 💰 Grants")
            for key in ["Canada Grant", "Dependent Grant", "Alberta Grant", "Canada Disability Grant", "Equipment Grant", "Alberta Disability Grant"]:
                if result[key] > 0:
                    st.write(f"{key}: {format_currency(result[key])}")

            st.write("### 🏦 Loans")
            st.write(f"Canada Loan: {format_currency(result['Canada Loan'])}")
            st.write(f"Alberta Loan: {format_currency(result['Alberta Loan'])}")

            st.markdown("---")
            st.subheader("🎓 Total Estimated Funding")
            st.markdown(f"<h2 style='color:#2E8B57'>{format_currency(result['Total Funding'])}</h2>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
