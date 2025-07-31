import streamlit as st
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Student Aid Estimator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    
    .step-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .result-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .total-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        text-align: center;
    }
    
    .progress-bar {
        background: #f0f0f0;
        border-radius: 10px;
        height: 20px;
        margin: 1rem 0;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    .metric-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'form_data' not in st.session_state:
    st.session_state.form_data = {
        'tuition_amount': '',
        'living_situation': '',
        'weeks_of_study': 34,
        'program_length': '',
        'family_income': '',
        'family_size': '',
        'is_independent': False,
        'dependents_under_12': 0,
        'has_disability': False,
        'disability_costs': ''
    }
if 'results' not in st.session_state:
    st.session_state.results = None

# Constants
LIVING_COSTS = {
    'pay-rent': 6920,  # $865/month × 8 = $6,920
    'dont-pay-rent': 6592  # $824/month × 8 = $6,592
}

def get_steps(has_disability):
    """Get the list of steps for the form"""
    base_steps = [
        {'id': 'tuition', 'title': 'Tuition & Fees', 'description': 'What is your tuition amount?'},
        {'id': 'living', 'title': 'Living Situation', 'description': 'Do you pay rent or not?'},
        {'id': 'weeks', 'title': 'Study Duration', 'description': 'How many weeks will you be studying?'},
        {'id': 'program_length', 'title': 'Program Length', 'description': 'How long is your program?'},
        {'id': 'income', 'title': 'Family Income', 'description': 'What is your family income?'},
        {'id': 'family', 'title': 'Family Size', 'description': 'How many people are in your family?'},
        {'id': 'independent', 'title': 'Student Status', 'description': 'Are you an independent student?'},
        {'id': 'dependents', 'title': 'Dependents', 'description': 'Do you have children under 12?'},
        {'id': 'disability', 'title': 'Disability Support', 'description': 'Do you have a permanent disability?'}
    ]
    
    if has_disability:
        base_steps.append({'id': 'disability_costs', 'title': 'Disability Costs', 'description': 'What are your disability-related costs?'})
    
    return base_steps

def validate_current_step():
    """Validate the current step's inputs"""
    steps = get_steps(st.session_state.form_data['has_disability'])
    current_step_data = steps[st.session_state.current_step]
    
    if current_step_data['id'] == 'tuition':
        if not st.session_state.form_data['tuition_amount'] or float(st.session_state.form_data['tuition_amount']) <= 0:
            st.error('Please enter a valid tuition amount')
            return False
    
    elif current_step_data['id'] == 'living':
        if not st.session_state.form_data['living_situation']:
            st.error('Please select your living situation')
            return False
    
    elif current_step_data['id'] == 'weeks':
        if not st.session_state.form_data['weeks_of_study'] or st.session_state.form_data['weeks_of_study'] < 1 or st.session_state.form_data['weeks_of_study'] > 52:
            st.error('Please enter a valid number of weeks (1-52)')
            return False
    
    elif current_step_data['id'] == 'program_length':
        if not st.session_state.form_data['program_length']:
            st.error('Please select your program length')
            return False
    
    elif current_step_data['id'] == 'income':
        if not st.session_state.form_data['family_income'] or float(st.session_state.form_data['family_income']) < 0:
            st.error('Please enter a valid family income')
            return False
    
    elif current_step_data['id'] == 'family':
        if not st.session_state.form_data['family_size'] or int(st.session_state.form_data['family_size']) < 1:
            st.error('Please enter a valid family size')
            return False
    
    elif current_step_data['id'] == 'dependents':
        if st.session_state.form_data['dependents_under_12'] < 0:
            st.error('Please enter a valid number of dependents')
            return False
    
    elif current_step_data['id'] == 'disability_costs':
        if st.session_state.form_data['has_disability'] and (not st.session_state.form_data['disability_costs'] or float(st.session_state.form_data['disability_costs']) < 0):
            st.error('Please enter a valid amount for disability costs')
            return False
    
    return True

def calculate_funding():
    """Calculate the funding based on form data"""
    # Get input values
    tuition = float(st.session_state.form_data['tuition_amount']) if st.session_state.form_data['tuition_amount'] else 0
    living_cost = LIVING_COSTS.get(st.session_state.form_data['living_situation'], 0)
    weeks = int(st.session_state.form_data['weeks_of_study']) if st.session_state.form_data['weeks_of_study'] else 34
    program_length = int(st.session_state.form_data['program_length']) if st.session_state.form_data['program_length'] else 1
    family_income = float(st.session_state.form_data['family_income']) if st.session_state.form_data['family_income'] else 0
    dependents_under_12 = int(st.session_state.form_data['dependents_under_12']) if st.session_state.form_data['dependents_under_12'] else 0
    disability_costs = float(st.session_state.form_data['disability_costs']) if st.session_state.form_data['disability_costs'] else 0

    # Fixed costs
    books_and_supplies = 1000
    computer = 500
    student_contribution = 1500

    # Calculate allowable costs and assessed need
    allowable_costs = tuition + books_and_supplies + computer + living_cost
    assessed_need = max(0, allowable_costs - student_contribution)

    # Calculate loans
    canada_student_loan = min(assessed_need * 0.6, 300 * weeks)
    max_total_loans = 8500 * (weeks / 17)  # $8,500 per 17 weeks
    alberta_student_loan = min(
        max(0, assessed_need - canada_student_loan),
        max_total_loans - canada_student_loan
    )

    # Calculate grants
    canada_full_time_grant = 0
    canada_dependent_grant = 0
    alberta_full_time_grant = 0

    # Income threshold for Canada grants
    income_threshold = 53318

    if program_length >= 2 and program_length <= 5 and family_income < income_threshold:
        canada_full_time_grant = 121.1538 * weeks
        canada_dependent_grant = 64.6153 * weeks * dependents_under_12
    elif program_length == 1:
        alberta_full_time_grant = 425 * (weeks / 4)

    # Disability grants
    canada_disability_grant = 0
    equipment_service_grant = 0
    alberta_disability_grant = 0

    if st.session_state.form_data['has_disability']:
        canada_disability_grant = 2800
        equipment_service_grant = min(disability_costs, 20000)
        alberta_disability_grant = min(max(0, disability_costs - 20000), 3000)

    # Calculate totals
    total_grants = (canada_full_time_grant + canada_dependent_grant + 
                   alberta_full_time_grant + canada_disability_grant + 
                   equipment_service_grant + alberta_disability_grant)
    total_loans = canada_student_loan + alberta_student_loan
    total_funding = total_grants + total_loans

    return {
        # Individual components
        'canada_student_loan': canada_student_loan,
        'alberta_student_loan': alberta_student_loan,
        'canada_full_time_grant': canada_full_time_grant,
        'canada_dependent_grant': canada_dependent_grant,
        'alberta_full_time_grant': alberta_full_time_grant,
        'canada_disability_grant': canada_disability_grant,
        'equipment_service_grant': equipment_service_grant,
        'alberta_disability_grant': alberta_disability_grant,
        
        # Totals
        'total_grants': total_grants,
        'total_loans': total_loans,
        'total_funding': total_funding,
        
        # Breakdown
        'breakdown': {
            'tuition': tuition,
            'books_and_supplies': books_and_supplies,
            'computer': computer,
            'living_cost': living_cost,
            'student_contribution': student_contribution,
            'allowable_costs': allowable_costs,
            'assessed_need': assessed_need,
            'max_total_loans': max_total_loans
        }
    }

def format_currency(amount):
    """Format amount as Canadian currency"""
    return f"${amount:,.2f}"

def render_step():
    """Render the current step"""
    steps = get_steps(st.session_state.form_data['has_disability'])
    step = steps[st.session_state.current_step]
    
    st.markdown(f"""
    <div class="step-header">
        <h2>{step['title']}</h2>
        <p>{step['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if step['id'] == 'tuition':
        st.session_state.form_data['tuition_amount'] = st.number_input(
            "Enter tuition amount (including fees)",
            min_value=0.0,
            step=100.0,
            value=float(st.session_state.form_data['tuition_amount']) if st.session_state.form_data['tuition_amount'] else 0.0,
            format="%.2f"
        )
    
    elif step['id'] == 'living':
        st.session_state.form_data['living_situation'] = st.selectbox(
            "Select your living situation",
            options=["", "pay-rent", "dont-pay-rent"],
            format_func=lambda x: {"": "Select your living situation", "pay-rent": "Pay Rent", "dont-pay-rent": "Don't Pay Rent"}[x],
            index=0 if not st.session_state.form_data['living_situation'] else ["pay-rent", "dont-pay-rent"].index(st.session_state.form_data['living_situation']) + 1
        )
    
    elif step['id'] == 'weeks':
        st.session_state.form_data['weeks_of_study'] = st.number_input(
            "Enter weeks of study",
            min_value=1,
            max_value=52,
            value=int(st.session_state.form_data['weeks_of_study']) if st.session_state.form_data['weeks_of_study'] else 34
        )
    
    elif step['id'] == 'program_length':
        st.session_state.form_data['program_length'] = st.selectbox(
            "Select program length",
            options=["", "1", "2", "3", "4", "5"],
            format_func=lambda x: {"": "Select program length", "1": "1 Year", "2": "2 Years", "3": "3 Years", "4": "4 Years", "5": "5 Years"}[x],
            index=0 if not st.session_state.form_data['program_length'] else int(st.session_state.form_data['program_length'])
        )
    
    elif step['id'] == 'income':
        st.session_state.form_data['family_income'] = st.number_input(
            "Enter family income (Line 15000)",
            min_value=0.0,
            step=1000.0,
            value=float(st.session_state.form_data['family_income']) if st.session_state.form_data['family_income'] else 0.0,
            format="%.2f"
        )
    
    elif step['id'] == 'family':
        st.session_state.form_data['family_size'] = st.number_input(
            "Number of family members",
            min_value=1,
            value=int(st.session_state.form_data['family_size']) if st.session_state.form_data['family_size'] else 1
        )
    
    elif step['id'] == 'independent':
        st.session_state.form_data['is_independent'] = st.checkbox(
            "I am an independent student",
            value=st.session_state.form_data['is_independent']
        )
    
    elif step['id'] == 'dependents':
        st.session_state.form_data['dependents_under_12'] = st.number_input(
            "Number of dependent children under 12",
            min_value=0,
            value=int(st.session_state.form_data['dependents_under_12']) if st.session_state.form_data['dependents_under_12'] else 0
        )
    
    elif step['id'] == 'disability':
        st.session_state.form_data['has_disability'] = st.checkbox(
            "I have a permanent disability",
            value=st.session_state.form_data['has_disability']
        )
    
    elif step['id'] == 'disability_costs':
        st.session_state.form_data['disability_costs'] = st.number_input(
            "Enter estimated cost of services/equipment",
            min_value=0.0,
            step=100.0,
            value=float(st.session_state.form_data['disability_costs']) if st.session_state.form_data['disability_costs'] else 0.0,
            format="%.2f"
        )

def main():
    # Header
    st.markdown('<h1 class="main-header">🎓 Student Aid Estimator</h1>', unsafe_allow_html=True)
    
    # Progress bar
    steps = get_steps(st.session_state.form_data['has_disability'])
    progress = (st.session_state.current_step + 1) / len(steps)
    
    st.markdown(f"""
    <div class="progress-bar">
        <div class="progress-fill" style="width: {progress * 100}%"></div>
    </div>
    <p style="text-align: center; margin: 1rem 0;">Step {st.session_state.current_step + 1} of {len(steps)}</p>
    """, unsafe_allow_html=True)
    
    # Handle disability status change
    if st.session_state.form_data['has_disability'] and st.session_state.current_step > 8:
        st.session_state.current_step = 8
    
    # Show results or form
    if st.session_state.results:
        # Display results
        st.markdown('<h2 style="text-align: center; margin-bottom: 2rem;">Your Funding Estimate</h2>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown('### 📊 Loans')
            
            col1a, col1b = st.columns(2)
            with col1a:
                st.metric("Canada Student Loan", format_currency(st.session_state.results['canada_student_loan']))
            with col1b:
                st.metric("Alberta Student Loan", format_currency(st.session_state.results['alberta_student_loan']))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown('### 💰 Grants')
            
            grants_data = []
            if st.session_state.results['canada_full_time_grant'] > 0:
                grants_data.append(("Canada Full-Time Grant", st.session_state.results['canada_full_time_grant']))
            if st.session_state.results['canada_dependent_grant'] > 0:
                grants_data.append(("Canada Dependent Grant", st.session_state.results['canada_dependent_grant']))
            if st.session_state.results['alberta_full_time_grant'] > 0:
                grants_data.append(("Alberta Full-Time Grant", st.session_state.results['alberta_full_time_grant']))
            if st.session_state.results['canada_disability_grant'] > 0:
                grants_data.append(("Canada Disability Grant", st.session_state.results['canada_disability_grant']))
            if st.session_state.results['equipment_service_grant'] > 0:
                grants_data.append(("Equipment/Service Grant", st.session_state.results['equipment_service_grant']))
            if st.session_state.results['alberta_disability_grant'] > 0:
                grants_data.append(("Alberta Disability Grant", st.session_state.results['alberta_disability_grant']))
            
            for grant_name, amount in grants_data:
                st.metric(grant_name, format_currency(amount))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown('### 📋 Cost Breakdown')
            
            breakdown = st.session_state.results['breakdown']
            st.metric("Tuition & Fees", format_currency(breakdown['tuition']))
            st.metric("Books & Supplies", format_currency(breakdown['books_and_supplies']))
            st.metric("Computer", format_currency(breakdown['computer']))
            st.metric("Living Costs", format_currency(breakdown['living_cost']))
            st.metric("Student Contribution", f"-{format_currency(breakdown['student_contribution'])}")
            st.metric("Assessed Need", format_currency(breakdown['assessed_need']))
            st.metric("Max Total Loans", format_currency(breakdown['max_total_loans']))
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Total funding summary
        st.markdown(f"""
        <div class="total-section">
            <h3>🎯 Total Funding Summary</h3>
            <div style="display: flex; justify-content: space-around; margin: 1rem 0;">
                <div>
                    <h4>Total Grants</h4>
                    <h2>{format_currency(st.session_state.results['total_grants'])}</h2>
                </div>
                <div>
                    <h4>Total Loans</h4>
                    <h2>{format_currency(st.session_state.results['total_loans'])}</h2>
                </div>
                <div>
                    <h4>Total Estimated Funding</h4>
                    <h2>{format_currency(st.session_state.results['total_funding'])}</h2>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Start over button
        if st.button("🔄 Start Over", type="primary"):
            st.session_state.current_step = 0
            st.session_state.results = None
            st.session_state.form_data = {
                'tuition_amount': '',
                'living_situation': '',
                'weeks_of_study': 34,
                'program_length': '',
                'family_income': '',
                'family_size': '',
                'is_independent': False,
                'dependents_under_12': 0,
                'has_disability': False,
                'disability_costs': ''
            }
            st.rerun()
    
    else:
        # Show form
        render_step()
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.session_state.current_step > 0:
                if st.button("← Previous"):
                    st.session_state.current_step -= 1
                    st.rerun()
        
        with col3:
            if st.session_state.current_step < len(steps) - 1:
                if st.button("Next →"):
                    if validate_current_step():
                        st.session_state.current_step += 1
                        st.rerun()
            else:
                if st.button("Estimate My Funding", type="primary"):
                    if validate_current_step():
                        st.session_state.results = calculate_funding()
                        st.rerun()

if __name__ == "__main__":
    main() 