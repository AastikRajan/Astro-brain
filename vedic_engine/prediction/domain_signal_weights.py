"""
Domain-specific signal weights from deep research.
Each domain has ranked primary/secondary signals with exact weights (1-10 scale).
Used by prediction pipeline to document priority signals.
"""

DOMAIN_SIGNALS = {
    "career": {
        "primary": [
            ("kp_sublord_10", 10.0),
            ("d10_10th_lord_placement", 9.5),
            ("vimshottari_dasha_10th_connection", 9.0),
            ("d10_10th_house_lord", 8.5),
            ("double_transit_10_1", 8.0),
        ],
        "secondary": [
            ("vimshopak_10th_lord", 7.5),
            ("raja_mahapurusha_yogas", 7.0),
            ("avastha_10th_lord", 7.0),
            ("bav_10th_sign", 6.5),
            ("sun_karaka_strength", 6.0),
        ],
    },
    "finance": {
        "primary": [
            ("11th_lord_strength", 10.0),
            ("2nd_lord_strength", 9.5),
            ("sav_11_and_2", 9.0),
            ("dasha_dhana_yoga_activation", 8.5),
            ("d2_hora_dignity", 8.0),
        ],
        "secondary": [
            ("daridra_yogas", 7.5),
            ("8th_house_linkage", 7.0),
            ("jupiter_strength", 6.5),
            ("12th_house_prominence", 6.0),
            ("2nd_vs_11th_comparison", 5.0),
        ],
    },
    "marriage": {
        "primary": [
            ("bvb_md_ad_1_7_connection", 10.0),
            ("d9_7th_house_lord_dignity", 10.0),
            ("bvb_lagna_7th_lord_connection", 9.8),
            ("chara_dasha_dk_ul_connection", 9.6),
            ("upapada_lagna_condition", 9.0),
        ],
        "secondary": [
            ("d1_7th_lord_placement", 8.5),
            ("double_transit_7_1", 8.5),
            ("darakaraka_condition", 7.5),
            ("venus_karaka_condition", 7.0),
            ("manglik_dosha", 6.0),
        ],
    },
    "health": {
        "primary": [
            ("lagna_lord_strength", 10.0),
            ("dasha_6_8_12_activation", 9.5),
            ("d30_trimsamsha_affliction", 9.0),
            ("moon_dignity", 8.5),
            ("maraka_lord_dasha", 8.0),
        ],
        "secondary": [
            ("8th_house_prominence", 7.5),
            ("6th_house_prominence", 7.0),
            ("sade_sati_active", 6.0),
            ("malefic_transit_lagna_moon", 6.0),
            ("12th_house_prominence", 5.5),
        ],
    },
}
