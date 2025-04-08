from typing import Dict, List
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
import pandas as pd
from pydantic import BaseModel
from schemas import DataRequest
from gemini import get_graph_suggestions, get_graph_suggestions_
from graph_gen import generate_graphs_zip  # <-- updated import
import logging
from report_generator import create_pdf_report

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
    expose_headers=["*"]  
)

from fastapi.responses import StreamingResponse

@app.post("/generate-graphs")
async def generate_graphs_endpoint(request: DataRequest):
    try:
        logger.info("Received request data")
        logger.info("Calling Gemini to get graph suggestions...")
        gemini_result = await get_graph_suggestions(request.data)

        suggestions = gemini_result["suggestions"]
        summary = gemini_result["summary"]

        logger.info("Generating graphs + summary zip...")
        zip_buffer = generate_graphs_zip(request.data, suggestions, summary)

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=generated_charts.zip"}
        )
    except Exception as e:
        logger.error(f"Error during /generate-graphs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class JSONData(BaseModel):
    records: List[Dict]

# @app.post("/generate-report")
# async def generate_report(request: DataRequest):
#     try:
#         logger.info("Generating in-memory PDF report...")
#         pdf_buffer = create_pdf_report(request.data)  # passing `data` list of dicts

#         return StreamingResponse(
#             pdf_buffer,
#             media_type="application/pdf",
#             headers={"Content-Disposition": "attachment; filename=report.pdf"}
#         )
#     except Exception as e:
#         logger.error(f"Error generating report: {e}")
#         raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/generate-report")
async def generate_report_endpoint(request: DataRequest):
    """Generate a PDF report with data analysis and visualizations"""
    try:
        logger.info("Received report generation request")
        logger.info("Calling Gemini to get insights...")
        # data = request.data
        notes = request.notes 
        gemini_response = await get_graph_suggestions_(request.data, notes)
        logger.info("Generating in-memory PDF report...")
        
        # Extract suggestions and summary from the Gemini response
        graph_suggestions = gemini_response.get("suggestions", [])
        summary = gemini_response.get("summary", "No summary provided.")
        
        # Generate PDF report with all required arguments
        pdf_buffer = create_pdf_report(request.data, graph_suggestions, summary)
        
        # Return PDF as a downloadable file
        return Response(
            content=pdf_buffer.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=business_report.pdf"}
        )
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))