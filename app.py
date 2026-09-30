import streamlit as st
import pandas as pd

# -------------------------------
# PAGE CONFIGURATION
# -------------------------------
st.set_page_config(
    page_title="Income Tax Calculator",
    page_icon="💰",
    layout="centered"
)

st.title("💰 Income Tax Calculator")
st.write("Calculate and compare your estimated income tax under the Old and New Tax Regimes across different Financial Years.")

# -------------------------------
# CONFIGURATION BY FINANCIAL YEAR
# -------------------------------
NEW_REGIME_CONFIG = {
    "FY 2025-26 (AY 2026-27)": {
        "standard_deduction": 75000,
        "rebate_limit": 1200000,
        "max_rebate": 60000,
        "slabs": [
            (400000, 0.00),
            (800000, 0.05),
            (1200000, 0.10),
            (1600000, 0.15),
            (2000000, 0.20),
            (2400000, 0.25),
            (float("inf"), 0.30)
        ],
        "highlights": "Budget 2025: Nil slab up to ₹4L, Sec 87A full rebate up to ₹12L taxable income (₹12.75L with Standard Deduction)."
    },
    "FY 2024-25 (AY 2025-26)": {
        "standard_deduction": 75000,
        "rebate_limit": 700000,
        "max_rebate": 25000,
        "slabs": [
            (300000, 0.00),
            (700000, 0.05),
            (1000000, 0.10),
            (1200000, 0.15),
            (1500000, 0.20),
            (float("inf"), 0.30)
        ],
        "highlights": "Budget July 2024: Standard deduction raised to ₹75,000. Full rebate up to ₹7L taxable income (₹7.75L for salaried)."
    },
    "FY 2023-24 (AY 2024-25)": {
        "standard_deduction": 50000,
        "rebate_limit": 700000,
        "max_rebate": 25000,
        "slabs": [
            (300000, 0.00),
            (600000, 0.05),
            (900000, 0.10),
            (1200000, 0.15),
            (1500000, 0.20),
            (float("inf"), 0.30)
        ],
        "highlights": "Budget 2023: New regime default, ₹50,000 Standard Deduction, Sec 87A rebate up to ₹7L."
    }
}

OLD_REGIME_CONFIG = {
    "standard_deduction": 50000,
    "rebate_limit": 500000,
    "max_rebate": 12500
}

# -------------------------------
# USER INPUTS
# -------------------------------
st.header("Enter Your Details")

# Financial Year Selection
financial_year = st.selectbox(
    "📅 Select Financial Year (FY)",
    options=list(NEW_REGIME_CONFIG.keys()),
    index=0,
    help="Select the financial year for which you want to calculate taxes."
)

st.caption(f"💡 **Highlights for {financial_year.split(' ')[0]}:** {NEW_REGIME_CONFIG[financial_year]['highlights']}")

col1, col2 = st.columns(2)

with col1:
    income = st.number_input(
        "Annual Gross Income (₹)",
        min_value=0,
        value=1000000,
        step=10000
    )

with col2:
    age = st.number_input(
        "Age",
        min_value=18,
        max_value=100,
        value=25,
        step=1
    )

is_salaried = st.checkbox(
    "Salaried Individual / Pensioner (Eligible for Standard Deduction)",
    value=True,
    help="Salaried individuals and pensioners are eligible for standard deduction."
)

regime = st.radio(
    "Select Tax Regime",
    ["New Tax Regime", "Old Tax Regime"],
    horizontal=True
)

# -------------------------------
# DEDUCTIONS
# -------------------------------
fy_new_config = NEW_REGIME_CONFIG[financial_year]

if regime == "Old Tax Regime":
    st.subheader("Deductions (Old Regime)")

    c_std, c_80c = st.columns(2)
    with c_std:
        std_ded_old = OLD_REGIME_CONFIG["standard_deduction"] if is_salaried else 0
        st.metric("Standard Deduction (Auto)", f"₹{std_ded_old:,.0f}")

    with c_80c:
        section_80C = st.number_input(
            "Section 80C - PPF, EPF, ELSS, LIC (Max ₹1,50,000)",
            min_value=0,
            max_value=150000,
            value=0,
            step=5000
        )

    c_80d, c_hra = st.columns(2)
    with c_80d:
        section_80D = st.number_input(
            "Section 80D - Health Insurance",
            min_value=0,
            value=0,
            step=5000
        )

    with c_hra:
        hra_other = st.number_input(
            "HRA / Home Loan Interest / Other Deductions",
            min_value=0,
            value=0,
            step=5000
        )

    total_deductions = std_ded_old + section_80C + section_80D + hra_other

else:
    # New Tax Regime deductions
    std_ded_new = fy_new_config["standard_deduction"] if is_salaried else 0
    total_deductions = std_ded_new

    st.info(
        f"ℹ️ Under the **New Tax Regime** for **{financial_year}**, "
        f"Standard Deduction is **₹{std_ded_new:,.0f}** for salaried individuals. "
        "Deductions like 80C, 80D, and HRA are not applicable."
    )

# -------------------------------
# TAX CALCULATION FUNCTIONS
# -------------------------------

def compute_tax_breakdown(taxable_income, slabs):
    tax = 0.0
    previous = 0
    breakdown = []

    for limit, rate in slabs:
        if taxable_income > previous:
            taxable_amount = min(taxable_income, limit) - previous
            slab_tax = taxable_amount * rate
            tax += slab_tax

            slab_label = f"₹{previous:,.0f} – ₹{limit:,.0f}" if limit != float("inf") else f"Above ₹{previous:,.0f}"
            breakdown.append({
                "Slab Range": slab_label,
                "Tax Rate": f"{int(rate * 100)}%",
                "Taxable Amount": f"₹{taxable_amount:,.0f}",
                "Tax Amount": f"₹{slab_tax:,.0f}"
            })

        if taxable_income <= limit:
            break

        previous = limit

    return tax, breakdown


def calculate_new_regime_tax(taxable_income, fy):
    config = NEW_REGIME_CONFIG[fy]
    base_tax, breakdown = compute_tax_breakdown(taxable_income, config["slabs"])

    # Section 87A Rebate & Marginal Relief
    rebate = 0.0
    rebate_note = ""

    if taxable_income <= config["rebate_limit"]:
        rebate = base_tax
        if rebate > 0:
            rebate_note = f"Full rebate u/s 87A applied (Taxable income ≤ ₹{config['rebate_limit']:,.0f})"
    else:
        # Marginal relief under Sec 87A: tax payable cannot exceed income above rebate limit
        excess_income = taxable_income - config["rebate_limit"]
        if base_tax > excess_income:
            rebate = base_tax - excess_income
            rebate_note = f"Marginal Relief u/s 87A applied (Tax capped to income above ₹{config['rebate_limit']:,.0f})"

    net_tax = max(0.0, base_tax - rebate)
    cess = net_tax * 0.04
    total_tax = round(net_tax + cess)

    return {
        "base_tax": base_tax,
        "rebate": rebate,
        "rebate_note": rebate_note,
        "net_tax": net_tax,
        "cess": cess,
        "total_tax": total_tax,
        "breakdown": breakdown
    }


def get_old_regime_slabs(age):
    if age < 60:
        return [
            (250000, 0.00),
            (500000, 0.05),
            (1000000, 0.20),
            (float("inf"), 0.30)
        ]
    elif age < 80:
        return [
            (300000, 0.00),
            (500000, 0.05),
            (1000000, 0.20),
            (float("inf"), 0.30)
        ]
    else:
        return [
            (500000, 0.00),
            (1000000, 0.20),
            (float("inf"), 0.30)
        ]


def calculate_old_regime_tax(taxable_income, age):
    slabs = get_old_regime_slabs(age)
    base_tax, breakdown = compute_tax_breakdown(taxable_income, slabs)

    # Section 87A Rebate for Old Regime (up to 12,500 for income <= 5,00,000)
    rebate = 0.0
    rebate_note = ""

    if taxable_income <= OLD_REGIME_CONFIG["rebate_limit"]:
        rebate = min(base_tax, OLD_REGIME_CONFIG["max_rebate"])
        if rebate > 0:
            rebate_note = "Full rebate u/s 87A applied (Taxable income ≤ ₹5,00,000)"

    net_tax = max(0.0, base_tax - rebate)
    cess = net_tax * 0.04
    total_tax = round(net_tax + cess)

    return {
        "base_tax": base_tax,
        "rebate": rebate,
        "rebate_note": rebate_note,
        "net_tax": net_tax,
        "cess": cess,
        "total_tax": total_tax,
        "breakdown": breakdown
    }


# -------------------------------
# CALCULATE BUTTON & RESULTS
# -------------------------------

if st.button("🧮 Calculate Income Tax", use_container_width=True, type="primary"):
    taxable_income = max(0, income - total_deductions)

    if regime == "New Tax Regime":
        result = calculate_new_regime_tax(taxable_income, financial_year)
    else:
        result = calculate_old_regime_tax(taxable_income, age)

    # -------------------------------
    # DISPLAY RESULTS
    # -------------------------------
    st.divider()
    st.header(f"📊 Tax Calculation ({financial_year})")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("Gross Income", f"₹{income:,.0f}")
        st.metric("Taxable Income", f"₹{taxable_income:,.0f}")

    with col_m2:
        st.metric("Total Deductions", f"₹{total_deductions:,.0f}")
        st.metric("Tax before Rebate", f"₹{result['base_tax']:,.0f}")

    col_m3, col_m4 = st.columns(2)
    with col_m3:
        st.metric("Sec 87A Rebate", f"- ₹{result['rebate']:,.0f}")

    with col_m4:
        st.metric("Health & Education Cess (4%)", f"₹{result['cess']:,.0f}")

    if result["rebate_note"]:
        st.success(f"🎉 **{result['rebate_note']}**")

    st.success(f"### 💰 Total Estimated Tax: ₹{result['total_tax']:,.0f}")

    # Key statistics
    effective_rate = (result["total_tax"] / income * 100) if income > 0 else 0
    monthly_tax = result["total_tax"] / 12

    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.info(f"Effective Tax Rate: **{effective_rate:.2f}%**")
    with col_stat2:
        st.info(f"Monthly Tax Provision: **₹{monthly_tax:,.0f}**")

    # -------------------------------
    # SLAB BREAKDOWN TABLE
    # -------------------------------
    with st.expander("🔍 View Slab-wise Tax Breakdown", expanded=False):
        if result["breakdown"]:
            df_breakdown = pd.DataFrame(result["breakdown"])
            st.table(df_breakdown)
        else:
            st.write("No tax liability in any slab.")

    # -------------------------------
    # REGIME COMPARISON SECTION
    # -------------------------------
    with st.expander(f"⚖️ Compare New vs Old Regime for {financial_year}", expanded=True):
        # Calculate other regime for comparison
        std_ded_old = OLD_REGIME_CONFIG["standard_deduction"] if is_salaried else 0
        taxable_income_old = max(0, income - (std_ded_old + (section_80C if regime == "Old Tax Regime" else 0) + (section_80D if regime == "Old Tax Regime" else 0) + (hra_other if regime == "Old Tax Regime" else 0)))
        
        std_ded_new = fy_new_config["standard_deduction"] if is_salaried else 0
        taxable_income_new = max(0, income - std_ded_new)

        res_new = calculate_new_regime_tax(taxable_income_new, financial_year)
        res_old = calculate_old_regime_tax(taxable_income_old, age)

        comp_col1, comp_col2 = st.columns(2)
        with comp_col1:
            st.markdown("#### New Tax Regime")
            st.write(f"- Deductions: **₹{std_ded_new:,.0f}**")
            st.write(f"- Taxable Income: **₹{taxable_income_new:,.0f}**")
            st.write(f"- Total Tax: **₹{res_new['total_tax']:,.0f}**")

        with comp_col2:
            st.markdown("#### Old Tax Regime")
            old_deds = income - taxable_income_old
            st.write(f"- Deductions: **₹{old_deds:,.0f}**")
            st.write(f"- Taxable Income: **₹{taxable_income_old:,.0f}**")
            st.write(f"- Total Tax: **₹{res_old['total_tax']:,.0f}**")

        diff = abs(res_new["total_tax"] - res_old["total_tax"])
        if res_new["total_tax"] < res_old["total_tax"]:
            st.success(f"💡 **Recommendation:** You save **₹{diff:,.0f}** by choosing the **New Tax Regime** in {financial_year.split(' ')[0]}!")
        elif res_old["total_tax"] < res_new["total_tax"]:
            st.success(f"💡 **Recommendation:** You save **₹{diff:,.0f}** by choosing the **Old Tax Regime** in {financial_year.split(' ')[0]}!")
        else:
            st.info("💡 **Both regimes result in the exact same tax liability.**")