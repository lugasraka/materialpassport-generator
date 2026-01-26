"""
Generate complete material passports.
"""
from datetime import datetime
from uuid import uuid4
from typing import Dict, Optional

class PassportService:
    """Generate and manage material passports"""
    
    def __init__(
        self,
        prediction_service,
        sustainability_service,
        mlflow_service=None
    ):
        self.prediction_service = prediction_service
        self.sustainability_service = sustainability_service
        self.mlflow_service = mlflow_service
        self.passports = {}  # In-memory storage for MVP
        
        print("PassportService initialized")
    
    def generate_passport(self, composition: dict, model_name: str = "xgboost") -> dict:
        """
        Generate complete material passport.
        
        Args:
            composition: Material composition dict
            model_name: Name of model to use (default: xgboost)
        
        Returns:
            Dict with complete passport data
        """
        try:
            # Get predictions
            strength_prediction = self.prediction_service.predict_strength(
                composition, model_name
            )
            recyclability_prediction = self.prediction_service.predict_recyclability(
                composition
            )
            
            # Calculate sustainability metrics
            recycled_content = self.sustainability_service.calculate_recycled_content(composition)
            circularity_score = self.sustainability_service.calculate_circularity_score(
                composition, recycled_content["materials"]
            )
            co2_emissions = self.sustainability_service.estimate_co2_emissions(composition)
            sustainability_grade = self.sustainability_service.assign_sustainability_grade({
                "circularity_score": circularity_score,
                "co2_emissions": co2_emissions
            })
            
            # Generate passport ID
            passport_id = str(uuid4())
            
            # Create passport data structure
            passport = {
                "id": passport_id,
                "material_type": "Concrete",
                "composition": composition,
                "predictions": {
                    "compressive_strength": strength_prediction,
                    "recyclability": recyclability_prediction
                },
                "sustainability_metrics": {
                    "circularity_score": circularity_score,
                    "co2_emissions": {
                        "value": co2_emissions,
                        "unit": "kg CO2/m³"
                    },
                    "recycled_content": recycled_content,
                    "sustainability_grade": sustainability_grade
                },
                "certification": "Circular Economy Compliant",
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "qr_code_url": f"/api/v1/passport/{passport_id}/qr"
            }
            
            # Store in database (in-memory for MVP)
            self.passports[passport_id] = passport
            
            print(f"✓ Generated passport: {passport_id}")
            return passport
            
        except Exception as e:
            print(f"✗ Error generating passport: {e}")
            raise
    
    def get_passport(self, passport_id: str) -> Optional[Dict]:
        """
        Retrieve stored passport by ID.
        
        Args:
            passport_id: Unique passport identifier
        
        Returns:
            Dict with passport data or None if not found
        """
        return self.passports.get(passport_id)
    
    def list_passports(self) -> list:
        """
        List all generated passports.
        
        Returns:
            List of passport dictionaries
        """
        return list(self.passports.values())
