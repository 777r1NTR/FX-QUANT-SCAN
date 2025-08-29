import streamlit as st

# App configuration - MUST BE ABSOLUTE FIRST
st.set_page_config(
    page_title="QuantFX Analytics Platform", 
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Safe imports with error handling
def safe_import():
    try:
        from viz.home import home
        return home, None
    except Exception as e:
        st.error(f"Error importing home: {e}")
        return None, str(e)

def safe_import_fx_heatmap():
    try:
        from viz.fx_heatmap import fx_heatmap
        return fx_heatmap, None
    except Exception as e:
        st.error(f"Error importing fx_heatmap: {e}")
        return None, str(e)

def safe_import_zone_locator():
    try:
        from viz.zone_locator import zone_locator
        return zone_locator, None
    except Exception as e:
        st.error(f"Error importing zone_locator: {e}")
        return None, str(e)

def safe_import_zone_transitions():
    try:
        from viz.zone_transitions import zone_transitions
        return zone_transitions, None
    except Exception as e:
        st.error(f"Error importing zone_transitions: {e}")
        return None, str(e)

def safe_import_strength_meter():
    try:
        from viz.strength_meter import strength_meter
        return strength_meter, None
    except Exception as e:
        st.info(f"Strength meter not available: {e}")
        return None, str(e)

def safe_import_fx_correlation():
    try:
        from viz.fx_correlation import fx_correlation
        return fx_correlation, None
    except Exception as e:
        st.info(f"FX correlation not available: {e}")
        return None, str(e)

# Import functions safely
home_func, home_error = safe_import()
fx_heatmap_func, fx_error = safe_import_fx_heatmap()
zone_locator_func, zl_error = safe_import_zone_locator()
zone_transitions_func, zt_error = safe_import_zone_transitions()
strength_meter_func, sm_error = safe_import_strength_meter()
fx_correlation_func, fc_error = safe_import_fx_correlation()

# Placeholder functions for missing components
def placeholder_strength_meter():
    st.title("💪 Currency Strength Meter")
    st.info("🚧 Strength Meter will be extracted from FX Heatmap soon!")
    st.markdown("""
    ### Coming Soon:
    - Individual currency strength analysis
    - Strength rankings and trends
    - Visual strength indicators
    """)

def placeholder_correlation():
    st.title("🔗 Correlation Tool")
    st.info("🚧 Correlation analysis tool coming soon!")
    st.markdown("""
    ### Planned Features:
    - Currency pair correlations
    - Correlation heatmaps
    - Historical correlation trends
    """)

def placeholder_zone_transitions():
    st.markdown("# 🚧 Zone Transitions")
    st.markdown("## 🟡 Coming Soon!")
    st.info("We're working on advanced zone transition tracking and alerts.")
    
    st.markdown("### This feature will include:")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("- 📊 **Real-time zone transition alerts**")
        st.markdown("- 📈 **Historical transition analysis**")
    
    with col2:
        st.markdown("- 🔔 **Breakout notifications**") 
        st.markdown("- 📋 **Transition probability scoring**")
    
    st.markdown("---")
    st.info("💡 Check back soon for updates!")
    
    # Add some current functionality metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🎯 Zone Locator, Correlation Matrix", "✅ Active")
    
    with col2:
        st.metric("📊 FX Heatmap, Strength Meter", "✅ Active")
    
    with col3:
        st.metric("🚧 Zone Transitions", "🔜 Beta")

# Clean 6-tab structure
TABS = {
    "🏠 Home": home_func or (lambda: st.error("Home not available")),
    "📊 FX Heatmap": fx_heatmap_func or (lambda: st.error("FX Heatmap not available")),
    "💪 Strength Meter": strength_meter_func or placeholder_strength_meter,
    "📍 Zone Locator(NEW!)": zone_locator_func or (lambda: st.error("Zone Locator not available")),
    "🔄 Zone Transitions(NEW!)": placeholder_zone_transitions,
    "🔗 Correlation Tool": fx_correlation_func or placeholder_correlation,
}

# Header
st.title("📈 QuantFX Research & Visualization Platform")
st.markdown("---")

# Show any import errors in sidebar
if any([home_error, fx_error, zl_error, zt_error]):
    with st.sidebar:
        st.warning("⚠️ Some components failed to load")
        if st.checkbox("Show error details"):
            if home_error: st.error(f"Home: {home_error}")
            if fx_error: st.error(f"FX Heatmap: {fx_error}")
            if zl_error: st.error(f"Zone Locator: {zl_error}")
            if zt_error: st.error(f"Zone Transitions: {zt_error}")

# Navigation
selected_tab = st.sidebar.selectbox("🧭 Navigate", list(TABS.keys()))

# Route to selected function
try:
    TABS[selected_tab]()
except Exception as e:
    st.error(f"Error loading {selected_tab}: {e}")
    st.write("**Debug info:**", str(e))
    
    # Show traceback for debugging
    import traceback
    st.code(traceback.format_exc())