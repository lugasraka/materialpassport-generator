"""
Calculate sustainability metrics from material composition.
Based on sustainability calculations from src/features/feature_engineering.py
"""
from typing import Dict

class SustainabilityService:
    """Calculate sustainability metrics for material passports"""
    
    def __init__(self):
        # CO2 emission factors (kg CO2 per kg of material)
        # Source: Emission factors from cement industry
        self.co2_factors = {
            "cement": 0.825,
            "blast_furnace_slag": 0.027,
            "fly_ash": 0.012,
            "water": 0.0,
            "superplasticizer": 0.5,
            "coarse_aggregate": 0.004,
            "fine_aggregate": 0.004
        }
    
    def calculate_circularity_score(self, composition: dict, recycled_materials: list) -> int:
        """
        Calculate 0-100 circularity score based on recycled content.
        
        Formula: weighted average of recycled content percentage and efficiency bonus.
        Recycled materials (circular economy) get 20% bonus.
        """
        total_mass = sum(composition.values())
        recycled_mass = sum([composition.get(mat, 0) for mat in recycled_materials if mat in composition])
        
        if total_mass == 0:
            return 0
        
        recycled_percentage = (recycled_mass / total_mass) * 100
        
        # Circularity formula: recycled % * 1.2 (bonus for using recycled materials)
        # Bonus accounts for the environmental benefit of using waste materials
        circularity = min(100, int(recycled_percentage * 1.2))
        
        return circularity
    
    def estimate_co2_emissions(self, composition: dict) -> float:
        """
        Estimate CO2 emissions in kg/m³ based on material composition.
        
        Formula: sum(material_amount * co2_factor for each material)
        """
        total_co2 = sum(
            self.co2_factors.get(mat, 0) * amount
            for mat, amount in composition.items()
        )
        return round(total_co2, 2)
    
    def calculate_recycled_content(self, composition: dict) -> dict:
        """
        Calculate percentage and types of recycled content.
        
        Recycled materials (circular economy):
        - Blast Furnace Slag: Industrial waste byproduct
        - Fly Ash: Coal combustion byproduct
        """
        recycled_materials = ["blast_furnace_slag", "fly_ash"]
        
        total_mass = sum(composition.values())
        recycled_mass = sum([composition.get(mat, 0) for mat in recycled_materials if mat in composition])
        
        if total_mass == 0:
            return {"percentage": 0, "materials": []}
        
        percentage = round((recycled_mass / total_mass) * 100, 1)
        
        materials_used = []
        if composition.get("blast_furnace_slag", 0) > 0:
            materials_used.append("Blast Furnace Slag")
        if composition.get("fly_ash", 0) > 0:
            materials_used.append("Fly Ash")
        
        return {"percentage": percentage, "materials": materials_used}
    
    def assign_sustainability_grade(self, metrics: dict) -> str:
        """
        Assign A-F grade based on circularity and CO2 emissions.
        
        Grading Rubric:
        A (Excellent): circularity >= 70 AND CO2 < 350
        B (Good): circularity >= 50 AND CO2 < 400
        C (Fair): circularity >= 30 AND CO2 < 500
        D (Poor): circularity >= 15
        F (Very Poor): circularity < 15
        """
        circularity = metrics.get("circularity_score", 0)
        co2_emissions = metrics.get("co2_emissions", 1000)
        
        # Grade A: Excellent sustainability
        if circularity >= 70 and co2_emissions < 350:
            return "A (Excellent)"
        
        # Grade B: Good sustainability
        elif circularity >= 50 and co2_emissions < 400:
            return "B (Good)"
        
        # Grade C: Fair sustainability
        elif circularity >= 30 and co2_emissions < 500:
            return "C (Fair)"
        
        # Grade D: Poor sustainability
        elif circularity >= 15:
            return "D (Poor)"
        
        # Grade F: Very Poor sustainability
        else:
            return "F (Very Poor)"
    
    def get_all_sustainability_metrics(self, composition: dict) -> dict:
        """
        Calculate all sustainability metrics for a given composition.
        
        Returns:
            - circularity_score: 0-100 scale
            - co2_emissions: kg CO2 per m³
            - recycled_content: percentage and material list
            - sustainability_grade: A-F grade
        """
        # Calculate recycled content
        recycled_content = self.calculate_recycled_content(composition)
        
        # Calculate circularity score
        circularity_score = self.calculate_circularity_score(
            composition,
            recycled_content["materials"]
        )
        
        # Estimate CO2 emissions
        co2_emissions = self.estimate_co2_emissions(composition)
        
        # Assign sustainability grade
        sustainability_grade = self.assign_sustainability_grade({
            "circularity_score": circularity_score,
            "co2_emissions": co2_emissions
        })
        
        return {
            "circularity_score": circularity_score,
            "co2_emissions": co2_emissions,
            "recycled_content": recycled_content,
            "sustainability_grade": sustainability_grade
        }
