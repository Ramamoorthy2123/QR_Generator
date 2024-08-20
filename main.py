# from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.responses import StreamingResponse
# from fastapi.middleware.cors import CORSMiddleware
# from pymongo import MongoClient
# import gridfs
# import qrcode
# from io import BytesIO
# import os
# import uuid

# app = FastAPI()

# # CORS Middleware setup
# origins = [
#     "http://www.neuroverse.co.in",  
#     "http://neuroverse.co.in",
#     "http://localhost:5173"
# ]


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # MongoDB setup
# # Update the connection string
# MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://ramamoorthy:WebDev@cluster0.mongodb.net/neurolabs?retryWrites=true&w=majority")
# client = MongoClient(MONGODB_URL)
# db = client["neurolabs"]
# fs = gridfs.GridFS(db)

# # Root endpoint
# @app.get("/")
# async def root():
#     return {"message": "Welcome to the File Upload and QR Code API"}

# # Helper function to generate QR code
# def generate_qr_code_data(file_url: str) -> BytesIO:
#     try:
#         qr = qrcode.QRCode()
#         qr.add_data(file_url)
#         qr.make(fit=True)
#         img = qr.make_image(fill='black', back='white')

#         buffer = BytesIO()
#         img.save(buffer)  # Save without format argument
#         buffer.seek(0)
#         return buffer
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"QR code generation failed: {str(e)}")
# @app.post("/upload")
# async def upload_file(file: UploadFile = File(...)):
#     try:
#         # Extract filename without extension
#         filename_without_ext = os.path.splitext(file.filename)[0]

#         # Check if a file with the same name already exists
#         existing_file = fs.find_one({"filename": filename_without_ext})
#         if existing_file:
#             # If it exists, return a message indicating that the file already exists
#             return {"message": "File already exists", "filename": filename_without_ext}

#         # Save file to GridFS
#         file_id = fs.put(file.file, filename=filename_without_ext)
#         return {"filename": filename_without_ext, "id": str(file_id)}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# # Retrieve file details endpoint
# @app.get("/files/{filename}")
# async def get_file(filename: str):
#     try:
#         file = fs.find_one({"filename": filename})
#         if not file:
#             raise HTTPException(status_code=404, detail="File not found")

#         file_url = f"http://www.neuroverse.co.in/download/{filename}"
#         return {"filename": filename, "file_url": file_url}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"File retrieval failed: {str(e)}")

# @app.get("/qrcode/{filename}")
# async def generate_qr_code(filename: str):
#     try:
#         file_url = f"http://www.neuroverse.co.in/download/{filename}"
#         qr_code_image = generate_qr_code_data(file_url)
#         return StreamingResponse(qr_code_image, media_type="image/png")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"QR code generation failed: {str(e)}")

# # Download file endpoint
# @app.get("/download/{filename}")
# async def download_file(filename: str):
#     try:
#         file = fs.find_one({"filename": filename})
#         if not file:
#             raise HTTPException(status_code=404, detail="File not found")

#         return StreamingResponse(file, media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={filename}"})
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"File download failed: {str(e)}")

# # Endpoint to list all files in the database
# @app.get("/files")
# async def list_files():
#     try:
#         # Retrieve all files stored in GridFS
#         files = fs.find()

#         # Prepare the list of file metadata
#         file_list = []
#         for file in files:
#             file_list.append({
#                 "filename": file.filename,
#                 "upload_date": file.upload_date,
#                 "file_id": str(file._id)
#             })

#         return file_list
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error retrieving file list: {str(e)}")
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from io import BytesIO
import qrcode
import os
from datetime import datetime

app = FastAPI()

# CORS Middleware setup
origins = [
    "https://neuroverse.co.in",
    "https://www.neuroverse.co.in",
    "https://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgreSQL setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:password@localhost/neurolabs")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the File model
class FileModel(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    upload_date = Column(TIMESTAMP, default=datetime.utcnow)
    file_data = Column(LargeBinary)

Base.metadata.create_all(bind=engine)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the File Upload and QR Code API"}

# Upload endpoint
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        db = SessionLocal()
        filename_without_ext = os.path.splitext(file.filename)[0]
        existing_file = db.query(FileModel).filter(FileModel.filename == filename_without_ext).first()
        if existing_file:
            db.close()
            return {"message": "File already exists", "filename": filename_without_ext}

        new_file = FileModel(filename=filename_without_ext, file_data=file.file.read())
        db.add(new_file)
        db.commit()
        db.refresh(new_file)
        db.close()
        return {"filename": filename_without_ext, "id": new_file.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# File details endpoint
@app.get("/files/{filename}")
async def get_file(filename: str):
    try:
        db = SessionLocal()
        file = db.query(FileModel).filter(FileModel.filename == filename).first()
        db.close()
        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        file_url = f"http://www.neuroverse.co.in/download/{filename}"
        return {"filename": filename, "file_url": file_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File retrieval failed: {str(e)}")

# QR code generation endpoint
@app.get("/qrcode/{filename}")
async def generate_qr_code(filename: str):
    try:
        file_url = f"http://www.neuroverse.co.in/download/{filename}"
        qr_code_image = generate_qr_code_data(file_url)
        return StreamingResponse(qr_code_image, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QR code generation failed: {str(e)}")

# Download file endpoint
@app.get("/download/{filename}")
async def download_file(filename: str):
    try:
        db = SessionLocal()
        file = db.query(FileModel).filter(FileModel.filename == filename).first()
        db.close()
        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        return StreamingResponse(BytesIO(file.file_data), media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={filename}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File download failed: {str(e)}")

# List files endpoint
@app.get("/files")
async def list_files():
    try:
        db = SessionLocal()
        files = db.query(FileModel).all()
        db.close()
        file_list = [{"filename": file.filename, "upload_date": file.upload_date, "file_id": file.id} for file in files]
        return file_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving file list: {str(e)}")

# Helper function to generate QR code
def generate_qr_code_data(file_url: str) -> BytesIO:
    try:
        qr = qrcode.QRCode()
        qr.add_data(file_url)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back='white')

        buffer = BytesIO()
        img.save(buffer)  # Save without format argument
        buffer.seek(0)
        return buffer
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QR code generation failed: {str(e)}")
