"""
Driver-Facing Field Responder Mobile View (PWA Simulator)
=========================================================
Rugged, high-contrast in-ambulance interface for first responders.
Supports regional Indian languages (Telugu, Tamil, Hindi, English),
tactile one-touch mission milestone buttons, and turn-by-turn road navigation.
"""
import streamlit as st
from typing import Dict, Any, List

try:
    import folium
    from streamlit_folium import st_folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False


# Localization dictionary for field responders
LOCALIZED_STRINGS = {
    "en": {
        "terminal_title": "AMBULANCE MOBILE DATA TERMINAL (MDT)",
        "unit_id": "Unit: AMB-VIZAG-01",
        "lang_label": "Regional Language",
        "mission_card_title": "ACTIVE DISPATCH MISSION",
        "mission_id": "Mission ID",
        "incident_type": "Emergency Type",
        "location": "Incident Site",
        "destination": "Hospital Destination",
        "eta": "Estimated Arrival",
        "victims": "Reported Victims",
        "severity": "Severity Level",
        "critical": "CRITICAL EMERGENCY",
        "action_accept": "1. ACCEPT MISSION",
        "action_en_route": "2. EN ROUTE (START GPS)",
        "action_patient_onboard": "3. PATIENT ONBOARD",
        "action_arrived": "4. ARRIVED AT HOSPITAL",
        "status_label": "Current Mission Status",
        "status_assigned": "ASSIGNED (Awaiting Driver)",
        "status_accepted": "ACCEPTED (Preparing Vehicle)",
        "status_en_route": "EN ROUTE (GPS Active)",
        "status_patient_onboard": "PATIENT ONBOARD (In-Transit to ICU)",
        "status_completed": "MISSION COMPLETED",
        "navigation_title": "Turn-by-Turn Road Guidance",
        "reset_btn": "Reset Demo Mission",
        "detour_alert": "⚠️ Dynamic Detour: Low-lying flooded road bypassed via Coastal Flyover.",
        "steps": [
            "Depart KGH Hospital depot heading north on Hospital Road (400 m)",
            "Turn left onto Jagadamba Commercial Avenue (1.2 km)",
            "⚠️ HAZARD AVOIDANCE: Take Coastal Flyover to bypass waterlogged underpass (1.8 km)",
            "Arrive at Disaster Site on right (200 m)"
        ]
    },
    "te": {
        "terminal_title": "అంబులెన్స్ మొబైల్ డేటా టెర్మినల్ (MDT)",
        "unit_id": "యూనిట్: AMB-VIZAG-01",
        "lang_label": "భాష",
        "mission_card_title": "ప్రస్తుత అత్యవసర మిషన్",
        "mission_id": "మిషన్ ఐడి",
        "incident_type": "ప్రమాద రకం",
        "location": "సంఘటన స్థలం",
        "destination": "గమ్యస్థాన ఆసుపత్రి",
        "eta": "చేరుకొనే సమయం",
        "victims": "బాధితుల సంఖ్య",
        "severity": "తీవ్రత స్థాయి",
        "critical": "తీవ్రమైన అత్యవసర పరిస్థితి",
        "action_accept": "1. మిషన్ అంగీకరించు",
        "action_en_route": "2. మార్గంలో ఉన్నాము (GPS ప్రారంభించు)",
        "action_patient_onboard": "3. రోగి అంబులెన్స్ లోకి ఎక్కించబడ్డారు",
        "action_arrived": "4. ఆసుపత్రికి చేరుకున్నాము",
        "status_label": "ప్రస్తుత స్థితి",
        "status_assigned": "కేటాయించబడింది (డ్రైవర్ కోసం వేచి ఉంది)",
        "status_accepted": "అంగీకరించబడింది (బయలుదేరడానికి సిద్ధం)",
        "status_en_route": "మార్గంలో ఉన్నాము (GPS యాక్టివ్)",
        "status_patient_onboard": "రోగి అంబులెన్స్ లో ఉన్నారు (ICU కి తరలింపు)",
        "status_completed": "మిషన్ విజయవంతంగా పూర్తయింది",
        "navigation_title": "దారి సూచనలు (టర్న్-బై-టర్న్)",
        "reset_btn": "మిషన్ రీసెట్ చేయండి",
        "detour_alert": "⚠️ దారి మళ్లింపు: వరద నీరు నిలిచిన రోడ్డును తప్పించి కోస్టల్ ఫ్లైఓవర్ మీదుగా రూట్ చేయబడింది.",
        "steps": [
            "KGH ఆసుపత్రి నుండి ఉత్తరం వైపు హాస్పిటల్ రోడ్డులో బయలుదేరండి (400 మీ)",
            "ఎడమవైపు జగదాంబ కమర్షియల్ అవెన్యూ లోకి తిరగండి (1.2 కి.మీ)",
            "⚠️ హెచ్చరిక: వరద నీటిని నివారించడానికి కోస్టల్ ఫ్లైఓవర్ మీదుగా వెళ్ళండి (1.8 కి.మీ)",
            "కుడివైపున ప్రమాద స్థలానికి చేరుకోండి (200 మీ)"
        ]
    },
    "ta": {
        "terminal_title": "ஆம்புலன்ஸ் மொபைல் தரவு முனையம் (MDT)",
        "unit_id": "பிரிவு: AMB-VIZAG-01",
        "lang_label": "மொழி",
        "mission_card_title": "செயலில் உள்ள அவசர பணி",
        "mission_id": "பணி எண்",
        "incident_type": "அவசர வகை",
        "location": "சம்பவ இடம்",
        "destination": "இலக்கு மருத்துவமனை",
        "eta": "மதிப்பிடப்பட்ட வருகை",
        "victims": "பாதிக்கப்பட்டவர்கள்",
        "severity": "தீவிர நிலை",
        "critical": "மிகவும் அவசரமானது",
        "action_accept": "1. பணியை ஏற்றுக்கொள்",
        "action_en_route": "2. புறப்பட்டோம் (GPS இயக்கு)",
        "action_patient_onboard": "3. நோயாளி ஏற்றப்பட்டார்",
        "action_arrived": "4. மருத்துவமனை அடைந்தோம்",
        "status_label": "தற்போதைய நிலை",
        "status_assigned": "ஒதுக்கப்பட்டது (டிரைவர் பார்வைக்கு)",
        "status_accepted": "ஏற்றுக்கொள்ளப்பட்டது (வாகனம் தயார்)",
        "status_en_route": "பயணத்தில் உள்ளது (GPS இயங்குகிறது)",
        "status_patient_onboard": "நோயாளி வாகனத்தில் உள்ளார்",
        "status_completed": "பணி வெற்றிகரமாக முடிந்தது",
        "navigation_title": "பாதை வழிகாட்டல்",
        "reset_btn": "பணியை மீட்டமைக்கவும்",
        "detour_alert": "⚠️ மாற்றுப்பாதை: வெள்ளம் சூழ்ந்த சாலையைத் தவிர்த்து மேம்பாலம் வழியாக மாற்றுப்பாதை அமைக்கப்பட்டுள்ளது.",
        "steps": [
            "மருத்துவமனையிலிருந்து வடக்கு நோக்கிச் செல்லவும் (400 மீ)",
            "இடதுபுறம் திரும்பி முக்கிய சாலையில் செல்லவும் (1.2 கி.மீ)",
            "⚠️ வெள்ளம் தவிர்ப்பு: மேம்பாலம் வழியாக செல்லவும் (1.8 கி.மீ)",
            "வலதுபுறம் சம்பவ இடத்திற்கு வரவும் (200 மீ)"
        ]
    },
    "hi": {
        "terminal_title": "एम्बुलेंस मोबाइल डेटा टर्मिनल (MDT)",
        "unit_id": "यूनिट: AMB-VIZAG-01",
        "lang_label": "भाषा",
        "mission_card_title": "सक्रिय आपातकालीन मिशन",
        "mission_id": "मिशन आईडी",
        "incident_type": "आपदा प्रकार",
        "location": "घटना स्थल",
        "destination": "गंतव्य अस्पताल",
        "eta": "पहुंचने का अनुमानित समय",
        "victims": "पीड़ितों की संख्या",
        "severity": "गंभीरता स्तर",
        "critical": "अत्यंत गंभीर आपातकाल",
        "action_accept": "1. मिशन स्वीकार करें",
        "action_en_route": "2. रवाना हो चुके हैं (GPS शुरू करें)",
        "action_patient_onboard": "3. मरीज को एम्बुलेंस में लिया गया",
        "action_arrived": "4. अस्पताल पहुंचे",
        "status_label": "वर्तमान मिशन स्थिति",
        "status_assigned": "आवंटित (चालक की प्रतीक्षा में)",
        "status_accepted": "स्वीकार किया गया (वाहन तैयार)",
        "status_en_route": "रास्ते में हैं (GPS सक्रिय)",
        "status_patient_onboard": "मरीज सवार (ICU की ओर अग्रसर)",
        "status_completed": "मिशन सफलतापूर्वक संपन्न",
        "navigation_title": "मोड़-दर-मोड़ सड़क निर्देश",
        "reset_btn": "मिशन रीसेट करें",
        "detour_alert": "⚠️ गतिशील डायवर्जन: जलभराव वाले अंडरपास से बचकर कोस्टल फ्लाईओवर से मार्ग तय किया गया।",
        "steps": [
            "KGH अस्पताल से उत्तर की ओर हॉस्पिटल रोड पर निकलें (400 मीटर)",
            "बाएं मुड़कर जगदम्बा कमर्शियल एवेन्यू पर जाएं (1.2 किमी)",
            "⚠️ डायवर्जन: बाढ़ प्रभावित अंडरपास से बचने के लिए फ्लाईओवर लें (1.8 किमी)",
            "दाहिनी ओर दुर्घटना स्थल पर पहुंचें (200 मीटर)"
        ]
    }
}


def render_driver_mobile_map(status: str) -> None:
    """Render high-contrast turn-by-turn map for mobile screen."""
    # Coordinates for demo: Start (KGH), End (Jagadamba), Detour waypoint
    start_pos = [17.7088, 83.3071]
    detour_pos = [17.7160, 83.3010]
    end_pos = [17.7120, 83.2979]

    if not HAS_FOLIUM:
        st.info("Map preview available (Folium loaded).")
        return

    m = folium.Map(
        location=[17.7120, 83.3030],
        zoom_start=15,
        tiles="CartoDB dark_matter"
    )

    # Route polyline
    route_coords = [start_pos, detour_pos, end_pos]
    folium.PolyLine(
        route_coords,
        color="#22c55e",
        weight=6,
        opacity=0.9,
        tooltip="Active Safe Detour Route"
    ).add_to(m)

    # Markers
    folium.Marker(
        start_pos,
        popup="Depot: KGH Hospital",
        icon=folium.Icon(color="blue", icon="plus", prefix="fa")
    ).add_to(m)

    folium.Marker(
        end_pos,
        popup="Emergency: Jagadamba Trapped Civilians",
        icon=folium.Icon(color="red", icon="exclamation", prefix="fa")
    ).add_to(m)

    folium.Marker(
        detour_pos,
        popup="Safe Coastal Flyover Waypoint",
        icon=folium.Icon(color="green", icon="arrow-up", prefix="fa")
    ).add_to(m)

    # Highlight bypassed flood hazard zone in translucent red
    folium.Circle(
        location=[17.7100, 83.3035],
        radius=180,
        color="#ef4444",
        fill=True,
        fill_color="#ef4444",
        fill_opacity=0.35,
        popup="Waterlogged Roadway (Bypassed)"
    ).add_to(m)

    st_folium(m, height=280, width=None, use_container_width=True, returned_objects=[])


def render_driver_mobile_view():
    """Main rendering function for in-ambulance driver interface."""
    if "driver_mission_status" not in st.session_state:
        st.session_state.driver_mission_status = "ASSIGNED"

    if "driver_lang" not in st.session_state:
        st.session_state.driver_lang = "en"

    # Language selection toolbar
    lang_col1, lang_col2 = st.columns([2, 3])
    with lang_col1:
        selected_lang = st.selectbox(
            "Language / భాష / மொழி / भाषा",
            options=["en", "te", "ta", "hi"],
            format_func=lambda x: {
                "en": "English (EN)",
                "te": "తెలుగు (Telugu)",
                "ta": "தமிழ் (Tamil)",
                "hi": "हिन्दी (Hindi)"
            }[x],
            index=["en", "te", "ta", "hi"].index(st.session_state.driver_lang)
        )
        st.session_state.driver_lang = selected_lang

    T = LOCALIZED_STRINGS.get(st.session_state.driver_lang, LOCALIZED_STRINGS["en"])

    # Smartphone Frame Container
    st.markdown(f"""
    <div style="max-width: 520px; margin: 0 auto; background: #0f172a; 
                border: 2px solid #334155; border-radius: 24px; padding: 18px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.8); font-family: 'Inter', sans-serif;">
        
        <!-- Top Status Bar -->
        <div style="display: flex; justify-content: space-between; align-items: center; 
                    border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; margin-bottom: 12px;">
            <div style="color: #22c55e; font-size: 0.75rem; font-weight: 700; display:flex; align-items:center; gap:6px;">
                <span style="height:8px; width:8px; background:#22c55e; border-radius:50%; display:inline-block;"></span>
                GPS LOCKED (5G)
            </div>
            <div style="color: #94a3b8; font-size: 0.75rem; font-weight: 600;">{T['unit_id']}</div>
        </div>

        <!-- Terminal Header -->
        <div style="text-align: center; margin-bottom: 14px;">
            <div style="color: #38bdf8; font-size: 0.85rem; font-weight: 800; letter-spacing: 0.05em;">
                {T['terminal_title']}
            </div>
        </div>

        <!-- Dispatch Mission Card -->
        <div style="background: rgba(30, 41, 59, 0.9); border-radius: 14px; padding: 14px; 
                    border: 1px solid rgba(255,255,255,0.1); margin-bottom: 14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="color:#64748b; font-size:0.75rem; font-weight:700;">{T['mission_id']}: MSN-AP-901</span>
                <span style="background:#ef4444; color:#fff; font-size:0.7rem; font-weight:800; 
                             padding:3px 8px; border-radius:12px;">{T['critical']}</span>
            </div>
            <div style="color:#f8fafc; font-size:1.05rem; font-weight:700; margin-bottom:4px;">
                {T['incident_type']}: Building Fire & Structural Collapse
            </div>
            <div style="color:#94a3b8; font-size:0.8rem; margin-bottom:6px;">
                📍 <b>{T['location']}:</b> Jagadamba Junction, Visakhapatnam
            </div>
            <div style="color:#94a3b8; font-size:0.8rem; margin-bottom:6px;">
                🏥 <b>{T['destination']}:</b> King George Hospital (Trauma ICU)
            </div>
            <div style="display:flex; gap:12px; margin-top:8px; padding-top:8px; border-top:1px dashed rgba(255,255,255,0.1);">
                <span style="color:#38bdf8; font-size:0.75rem;">⏱️ <b>{T['eta']}:</b> 4.8 min</span>
                <span style="color:#f59e0b; font-size:0.75rem;">👥 <b>{T['victims']}:</b> 3 Trapped</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mission Status Pill
    current_status = st.session_state.driver_mission_status
    status_text_map = {
        "ASSIGNED": T["status_assigned"],
        "ACCEPTED": T["status_accepted"],
        "EN_ROUTE": T["status_en_route"],
        "PATIENT_ONBOARD": T["status_patient_onboard"],
        "COMPLETED": T["status_completed"]
    }
    status_color_map = {
        "ASSIGNED": "#3b82f6",
        "ACCEPTED": "#06b6d4",
        "EN_ROUTE": "#f59e0b",
        "PATIENT_ONBOARD": "#a855f7",
        "COMPLETED": "#22c55e"
    }

    st.markdown(f"""
    <div style="max-width: 520px; margin: 10px auto; text-align: center;">
        <div style="background: rgba(15, 23, 42, 0.9); border: 1px solid {status_color_map[current_status]}; 
                    border-radius: 12px; padding: 8px 12px; display: inline-block;">
            <span style="color: #94a3b8; font-size: 0.75rem; text-transform: uppercase;">{T['status_label']}:</span>
            <span style="color: {status_color_map[current_status]}; font-size: 0.85rem; font-weight: 800; margin-left: 6px;">
                {status_text_map[current_status]}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tactile Action Buttons (Sequential Workflow)
    btn_container = st.container()
    with btn_container:
        st.markdown("<div style='max-width:520px; margin:0 auto;'>", unsafe_allow_html=True)
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if current_status == "ASSIGNED":
                if st.button(f"🟢 {T['action_accept']}", use_container_width=True, key="btn_acc"):
                    st.session_state.driver_mission_status = "ACCEPTED"
                    st.rerun()
            elif current_status == "ACCEPTED":
                if st.button(f"🟡 {T['action_en_route']}", use_container_width=True, key="btn_enr"):
                    st.session_state.driver_mission_status = "EN_ROUTE"
                    st.rerun()
            else:
                st.button(f"✅ {T['action_accept']}", disabled=True, use_container_width=True)

        with col_b2:
            if current_status == "EN_ROUTE":
                if st.button(f"🟠 {T['action_patient_onboard']}", use_container_width=True, key="btn_pob"):
                    st.session_state.driver_mission_status = "PATIENT_ONBOARD"
                    st.rerun()
            elif current_status == "PATIENT_ONBOARD":
                if st.button(f"🔴 {T['action_arrived']}", use_container_width=True, key="btn_arr"):
                    st.session_state.driver_mission_status = "COMPLETED"
                    st.rerun()
            elif current_status == "COMPLETED":
                if st.button(f"🔄 {T['reset_btn']}", use_container_width=True, key="btn_rst"):
                    st.session_state.driver_mission_status = "ASSIGNED"
                    st.rerun()
            else:
                st.button(f"⏳ {T['action_patient_onboard']}", disabled=True, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Turn-by-Turn Map & Navigation Guidance
    st.markdown(f"""
    <div style="max-width: 520px; margin: 14px auto 8px auto;">
        <div style="color: #f1f5f9; font-size: 0.9rem; font-weight: 700; margin-bottom: 6px;">
            🧭 {T['navigation_title']}
        </div>
        <div style="background: rgba(239, 68, 68, 0.15); border-left: 3px solid #ef4444; 
                    padding: 8px 12px; border-radius: 4px; font-size: 0.75rem; color: #fca5a5; margin-bottom: 10px;">
            {T['detour_alert']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Render Map inside mobile width
    map_box = st.container()
    with map_box:
        st.markdown("<div style='max-width:520px; margin:0 auto;'>", unsafe_allow_html=True)
        render_driver_mobile_map(current_status)
        st.markdown("</div>", unsafe_allow_html=True)

    # Turn-by-turn list
    st.markdown("<div style='max-width:520px; margin:10px auto;'>", unsafe_allow_html=True)
    for idx, step_text in enumerate(T["steps"], 1):
        st.markdown(f"""
        <div style="display:flex; align-items:flex-start; gap:10px; background:rgba(30,41,59,0.7); 
                    border-radius:8px; padding:8px 10px; margin-bottom:6px; border:1px solid rgba(255,255,255,0.05);">
            <div style="background:#3b82f6; color:#fff; font-size:0.7rem; font-weight:800; 
                        min-width:20px; height:20px; border-radius:50%; display:flex; align-items:center; justify-content:center;">
                {idx}
            </div>
            <div style="color:#e2e8f0; font-size:0.8rem; line-height:1.4;">
                {step_text}
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
