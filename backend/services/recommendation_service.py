"""
Recommendation Service
Responsible solely for generating AI Controller Recommendations based on delay severity and operational context.
"""

class RecommendationService:
    def generate_recommendations(self, delay_status: str, context: dict = None) -> list:
        context = context or {}
        weather = context.get("weather", "").lower()
        track_status = context.get("track_status", "").lower()
        
        recommendations = []
        
        if delay_status == "ON TIME":
            recommendations.append("Proceed as scheduled.")
            recommendations.append("Maintain standard track speed.")
        elif delay_status == "MINOR DELAY":
            recommendations.append("Notify next station controller.")
            recommendations.append("Monitor train speed closely.")
            if "fog" in weather:
                recommendations.append("Activate high-visibility fog signaling.")
        elif delay_status == "MODERATE DELAY":
            recommendations.append("Notify next station controller.")
            recommendations.append("Issue passenger automated announcement.")
            recommendations.append("Increase signal priority at upcoming junction.")
            recommendations.append("Prepare platform staff for fast turnaround.")
        else: # CRITICAL DELAY
            recommendations.append("Activate emergency traffic management protocol.")
            recommendations.append("Reschedule affected follower trains.")
            recommendations.append("Inform Central Railway Control Room.")
            recommendations.append("Passenger assistance team required at station.")
            if "occupied" in track_status:
                recommendations.append("Initiate track re-routing to secondary loop line.")

        return recommendations

recommendation_service = RecommendationService()
