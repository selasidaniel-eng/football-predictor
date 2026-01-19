"""WeatherData model for storing match weather conditions"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from ..database import Base


class WeatherData(Base):
    """WeatherData model - stores weather conditions for matches"""

    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, unique=True, index=True)
    
    # Temperature
    temperature_celsius = Column(Float, nullable=True)
    feels_like_celsius = Column(Float, nullable=True)
    
    # Precipitation
    humidity = Column(Float, nullable=True)  # 0-100
    precipitation_mm = Column(Float, nullable=True)
    rain_probability = Column(Float, nullable=True)  # 0-100
    
    # Wind
    wind_speed_kmh = Column(Float, nullable=True)
    wind_direction = Column(String(50), nullable=True)  # N, NE, E, etc.
    wind_gust_kmh = Column(Float, nullable=True)
    
    # Conditions
    condition = Column(String(100), nullable=True)  # Clear, Cloudy, Rainy, etc.
    visibility_km = Column(Float, nullable=True)
    uv_index = Column(Float, nullable=True)
    
    # Field conditions
    pitch_condition = Column(String(50), default="normal", nullable=False)  # normal, wet, waterlogged
    field_temperature = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<WeatherData match_id={self.match_id} temp={self.temperature_celsius}°C>"
