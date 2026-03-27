from database import engine
import models

# Create all tables according to the new models
models.Base.metadata.create_all(bind=engine)

print("Normalized demo database initialized successfully.")
