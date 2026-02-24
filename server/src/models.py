"""
SQLAlchemy database models for prediction persistence.
"""
from datetime import datetime, timezone
from .extensions import db


class PredictionLog(db.Model):
    """Stores prediction results for analytics and history."""
    __tablename__ = 'prediction_logs'

    id = db.Column(db.Integer, primary_key=True)
    disease_type = db.Column(db.String(50), nullable=False, index=True)
    input_data = db.Column(db.JSON, nullable=False)
    prediction = db.Column(db.Integer, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    confidence = db.Column(db.Float, nullable=True)
    advice = db.Column(db.Text, nullable=True)
    shap_contributions = db.Column(db.JSON, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    def to_dict(self):
        return {
            'id': self.id,
            'disease_type': self.disease_type,
            'prediction': self.prediction,
            'risk_level': self.risk_level,
            'confidence': self.confidence,
            'advice': self.advice,
            'shap_contributions': self.shap_contributions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<PredictionLog {self.id} {self.disease_type} {self.risk_level}>'
