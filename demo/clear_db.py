from database import engine
import models

# Drop all tables to clear data
models.Base.metadata.drop_all(bind=engine)

# Recreate all tables
models.Base.metadata.create_all(bind=engine)

print("Database cleared successfully.")
