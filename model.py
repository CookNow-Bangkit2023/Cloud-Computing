from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
Base = declarative_base()
class Recipe(Base):
    __tablename__ = 'recipes'
    
    name = Column(Text)
    id = Column(Integer, primary_key=True)
    minutes = Column(Integer)
    contributor_id = Column(Integer)
    submitted = Column(Text)
    tags = Column(Text)
    nutrition = Column(Text)
    n_steps = Column(Integer)
    steps = Column(Text)
    description = Column(Text)
    ingredients = Column(Text)
    n_ingredients = Column(Integer)
class UserRecipeRating(Base):
    __tablename__ = 'user_recipe_ratings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255))
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    recipe = relationship("Recipe")
    date = Column(Date)
    rating = Column(Integer)