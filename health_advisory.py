"""
health_advisory.py
Health guidance keyed to the Indian AQI category displayed by AirWatch India.
These are general precautions, not a medical diagnosis.
"""

def get_advisory_by_category(category):
    """Return the health-advisory fields expected by app.py."""
    raw = str(category or "").strip().lower()
    normalized = raw.replace("🟢", "").replace("🟡", "").replace("🟠", "")
    normalized = normalized.replace("🔴", "").replace("🟣", "").replace("🟤", "").strip()

    # Match common names used by Indian AQI dashboards.
    if "good" in normalized:
        key = "good"
    elif "satisfactory" in normalized:
        key = "satisfactory"
    elif "moderate" in normalized:
        key = "moderate"
    elif "poor" in normalized and "very" not in normalized:
        key = "poor"
    elif "very poor" in normalized or "verypoor" in normalized:
        key = "very_poor"
    elif "severe" in normalized:
        key = "severe"
    else:
        key = "unknown"

    advisories = {
        "good": {
            "health_impact": "Air quality is considered satisfactory, with little or no risk for most people.",
            "general_public": "Enjoy usual outdoor activities while staying aware of changing conditions.",
            "sensitive_groups": "People who are unusually sensitive to air pollution should monitor symptoms.",
            "masks": "A mask is generally not needed solely because of this AQI reading."
        },
        "satisfactory": {
            "health_impact": "Air quality may cause minor breathing discomfort to sensitive people.",
            "general_public": "Most people can continue normal outdoor activities.",
            "sensitive_groups": "People with asthma or heart/lung conditions, children, and older adults should monitor symptoms and reduce prolonged strenuous activity if affected.",
            "masks": "Consider reducing exposure if you notice symptoms; a well-fitting N95/FFP2 can help reduce particle exposure outdoors."
        },
        "moderate": {
            "health_impact": "Some people with asthma or heart/lung conditions may experience breathing discomfort.",
            "general_public": "Limit prolonged or heavy outdoor exertion if you experience irritation or breathing symptoms.",
            "sensitive_groups": "Children, older adults, and people with asthma or heart/lung conditions should reduce prolonged strenuous outdoor activity.",
            "masks": "Consider a well-fitting N95/FFP2 outdoors when particle pollution is elevated; it does not protect against all gases."
        },
        "poor": {
            "health_impact": "Prolonged exposure may cause breathing discomfort for many people.",
            "general_public": "Reduce prolonged or strenuous outdoor activity and consider moving exercise indoors.",
            "sensitive_groups": "Children, older adults, pregnant people, and those with heart or lung conditions should minimize outdoor exertion.",
            "masks": "A well-fitting N95/FFP2 can reduce exposure to airborne particles outdoors; follow local public-health advice."
        },
        "very_poor": {
            "health_impact": "Prolonged exposure can increase the risk of respiratory illness and aggravate existing conditions.",
            "general_public": "Avoid strenuous outdoor activity and keep outdoor exposure as short as practical.",
            "sensitive_groups": "Sensitive groups should stay indoors where air is cleaner and follow clinician or public-health advice.",
            "masks": "If going outdoors is unavoidable, use a well-fitting N95/FFP2 for particle pollution; improve indoor ventilation/filtration where appropriate."
        },
        "severe": {
            "health_impact": "Air pollution at this level can affect healthy people and seriously affect people with existing illnesses.",
            "general_public": "Avoid outdoor exertion and minimize time outside; follow official local advisories.",
            "sensitive_groups": "Remain in cleaner indoor air as much as possible and seek medical advice for significant or worsening symptoms.",
            "masks": "If exposure is unavoidable, a well-fitting N95/FFP2 may reduce particle exposure, but it is not a substitute for avoiding polluted air."
        },
        "unknown": {
            "health_impact": "A reliable advisory could not be matched to this AQI category.",
            "general_public": "Check the displayed AQI category and the latest local public-health guidance.",
            "sensitive_groups": "People with heart or lung conditions, children, and older adults should be cautious when air quality is uncertain.",
            "masks": "Use official air-quality guidance to decide whether a well-fitting particle respirator is appropriate."
        }
    }
    return advisories[key]
