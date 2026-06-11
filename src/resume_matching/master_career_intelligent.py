from src.resume_matching.career_intelligence import (
    interpret_match_score ,
    identify_strength_areas,
    identify_weakness_areas ,
    learning_direction 
)

def career_intelligence_pipeline(ats_result):
    match = interpret_match_score(ats_result['Coverage'])
    strength = identify_strength_areas(ats_result['Matched'])
    weakness = identify_weakness_areas(ats_result['Missing'])
    direction = learning_direction(ats_result['Missing'])
    final_insight = (

        f"{match}\n\n"

        f"{strength}\n\n"

        f"{weakness}\n\n"

        f"{direction}"
    )
    return final_insight

