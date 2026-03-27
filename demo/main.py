import io
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
import os
import models
import services
from database import engine, get_db
import secrets

# 认证配置
VALID_USERS = {
    "admin": "admin123",
    "user": "user123"
}

security = HTTPBasic()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = credentials.username in VALID_USERS
    correct_password = secrets.compare_digest(
        credentials.password, 
        VALID_USERS.get(credentials.username, "")
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Normalized Business Data Import API (Demo)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for demo
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)

@app.get("/")
async def read_index():
    return FileResponse('index.html')

@app.get("/get_statistics.js")
async def get_stats_js():
    return FileResponse('get_statistics.js')

@app.post("/import/")
async def import_data(
    file: UploadFile = File(...),
    schema_type: str = Query(..., description="Type of schema"),
    snapshot_year: int = Query(None, description="Snapshot year"),
    snapshot_month: int = Query(None, description="Snapshot month"),
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username)
):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid file format.")
    contents = await file.read()
    try:
        count = services.process_excel_import(db, contents, schema_type, snapshot_year, snapshot_month)
        return {"detail": f"Successfully imported {count} records."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bulk_import/")
async def bulk_import_data(
    files: list[UploadFile] = File(...),
    schema_type: str = Query(..., description="Type of schema"),
    snapshot_years: list[str] = File(..., description="Snapshot years"),
    snapshot_months: list[str] = File(..., description="Snapshot months"),
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username)
):
    total_count = 0
    for i in range(len(files)):
        file = files[i]
        snapshot_year = int(snapshot_years[i])
        snapshot_month = int(snapshot_months[i])
        contents = await file.read()
        try:
            count = services.process_excel_import(db, contents, schema_type, snapshot_year, snapshot_month)
            total_count += count
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error in {file.filename}: {str(e)}")
    return {"detail": f"Successfully imported total of {total_count} records."}

@app.post("/sync/")
async def sync_data(db: Session = Depends(get_db), username: str = Depends(get_current_username)):
    try:
        count = services.sync_all_business_data(db)
        return {"detail": f"Successfully synchronized {count} companies."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete/")
async def delete_data(
    snapshot_year: int = Query(..., description="Snapshot year"),
    snapshot_month: int = Query(..., description="Snapshot month"),
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username)
):
    try:
        services.delete_data(db, snapshot_year, snapshot_month)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return {"detail": "Data deleted successfully."}

@app.get("/statistics/")
async def get_statistics(
    snapshot_year: int = Query(..., description="Snapshot year"),
    snapshot_month: int = Query(..., description="Snapshot month"),
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username)
):
    try:
        return services.get_statistics(db, snapshot_year, snapshot_month)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data_status/")
async def get_data_status(
    snapshot_year: int = Query(..., description="Snapshot year"),
    snapshot_month: int = Query(..., description="Snapshot month"),
    limit: int = Query(None, description="Max records"),
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username)
):
    try:
        return services.get_data_status(db, snapshot_year, snapshot_month, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export_data_status/")
async def export_data_status(
    snapshot_year: int = Query(..., description="Snapshot year"),
    snapshot_month: int = Query(..., description="Snapshot month"),
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username)
):
    try:
        buffer = services.export_data_status_to_excel(db, snapshot_year, snapshot_month)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=data_status_{snapshot_year}_{snapshot_month}.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
