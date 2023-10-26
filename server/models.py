from sqlalchemy.sql import func
from . import db

class VideoResult(db.Model):
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(100), nullable=False)
    paragraph_summary = db.Column(db.String(5000), nullable=False)
    similar_video_idea_summary = db.Column(db.String(5000), nullable=False)
    possible_tags = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=func.now())
    # result = db.Column(db.String(100), nullable=False)