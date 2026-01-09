"""
FastAPI application for GitHub Candidate Analyzer

This module provides the web interface for the analyzer.
It handles form submission, progress tracking, and report display.
"""

from fastapi import FastAPI, Form, BackgroundTasks, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.exceptions import HTTPException
import uuid
import json
import os
from pathlib import Path
from datetime import datetime

from .agent import GitHubAnalyzer

# Initialize FastAPI app
app = FastAPI(
    title="GitHub Candidate Analyzer",
    description="Analyze GitHub profiles for technical recruiting",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


def run_analysis_task(analysis_id: str, username: str, job_desc: str, context: str):
    """
    Background task to run the agent analysis.

    This function is executed in the background while the user sees progress updates.

    Args:
        analysis_id: Unique ID for this analysis
        username: GitHub username
        job_desc: Job description
        context: Additional context
    """
    try:
        # Update status to starting
        update_status(analysis_id, "starting", 0)

        # Create and run the analyzer
        analyzer = GitHubAnalyzer(analysis_id)
        result = analyzer.run(username, job_desc, context)

        # Mark as completed
        update_status(analysis_id, "completed", 100)

    except Exception as e:
        # On error, save error status
        update_status(analysis_id, "error", 0, error=str(e))
        print(f"Analysis {analysis_id} failed: {e}")


def update_status(analysis_id: str, stage: str, progress: int, **kwargs):
    """
    Update the analysis status file.

    Args:
        analysis_id: Analysis ID
        stage: Current stage name
        progress: Progress percentage (0-100)
        **kwargs: Additional status fields
    """
    status = {
        "stage": stage,
        "progress": progress,
        "timestamp": datetime.now().isoformat(),
        **kwargs
    }

    status_path = f"analyses/{analysis_id}/status.json"
    os.makedirs(os.path.dirname(status_path), exist_ok=True)

    with open(status_path, "w") as f:
        json.dump(status, f, indent=2)


def get_status(analysis_id: str) -> dict:
    """
    Get the current status of an analysis.

    Args:
        analysis_id: Analysis ID

    Returns:
        dict with status information
    """
    status_path = f"analyses/{analysis_id}/status.json"

    try:
        with open(status_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "stage": "not_found",
            "progress": 0,
            "error": "Analysis not found"
        }


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Homepage with input form.

    Returns:
        HTML template with the analysis form
    """
    return templates.TemplateResponse("index.html", {
        "request": request
    })


@app.post("/analyze")
async def start_analysis(
    background_tasks: BackgroundTasks,
    username: str = Form(..., min_length=1, max_length=100),
    job_description: str = Form(..., min_length=50),
    additional_context: str = Form(default="")
):
    """
    Start a new analysis.

    Args:
        background_tasks: FastAPI background tasks
        username: GitHub username (required)
        job_description: Job description (required, min 50 chars)
        additional_context: Additional context (optional)

    Returns:
        JSON with analysis_id and redirect_url
    """
    # Validate username (basic check)
    if not username.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub username format"
        )

    # Generate unique analysis ID
    analysis_id = str(uuid.uuid4())

    # Create analysis directory
    os.makedirs(f"analyses/{analysis_id}", exist_ok=True)

    # Start analysis in background
    background_tasks.add_task(
        run_analysis_task,
        analysis_id,
        username,
        job_description,
        additional_context
    )

    return JSONResponse({
        "analysis_id": analysis_id,
        "redirect_url": f"/results/{analysis_id}"
    })


@app.get("/status/{analysis_id}")
async def check_status(analysis_id: str):
    """
    Check the status of an analysis (for polling).

    Args:
        analysis_id: Analysis ID

    Returns:
        JSON with current status
    """
    return get_status(analysis_id)


@app.get("/results/{analysis_id}", response_class=HTMLResponse)
async def show_results(analysis_id: str, request: Request):
    """
    Show analysis results or progress.

    If analysis is complete, shows the report.
    If still running, shows progress page.

    Args:
        analysis_id: Analysis ID
        request: FastAPI request

    Returns:
        HTML template (either progress or results)
    """
    status = get_status(analysis_id)

    if status["stage"] == "completed":
        # Analysis complete - load and show report
        report_path = f"analyses/{analysis_id}/report.md"

        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report_md = f.read()

            return templates.TemplateResponse("results.html", {
                "request": request,
                "analysis_id": analysis_id,
                "report_markdown": report_md
            })

        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail="Report not found"
            )

    elif status["stage"] == "error":
        # Analysis failed - show error
        return templates.TemplateResponse("error.html", {
            "request": request,
            "analysis_id": analysis_id,
            "error": status.get("error", "Unknown error occurred")
        })

    else:
        # Still running - show progress
        return templates.TemplateResponse("progress.html", {
            "request": request,
            "analysis_id": analysis_id,
            "status": status
        })


@app.get("/export/{analysis_id}/pdf")
async def export_pdf(analysis_id: str):
    """
    Export analysis as PDF.

    Args:
        analysis_id: Analysis ID

    Returns:
        PDF file download
    """
    from .utils.export import generate_pdf

    try:
        pdf_path = generate_pdf(analysis_id)

        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"github_analysis_{analysis_id[:8]}.pdf"
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )


@app.get("/export/{analysis_id}/docx")
async def export_docx(analysis_id: str):
    """
    Export analysis as Word document.

    Args:
        analysis_id: Analysis ID

    Returns:
        Word document download
    """
    from .utils.export import generate_docx

    try:
        docx_path = generate_docx(analysis_id)

        return FileResponse(
            docx_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"github_analysis_{analysis_id[:8]}.docx"
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Word generation failed: {str(e)}"
        )


@app.get("/export/{analysis_id}/markdown")
async def export_markdown(analysis_id: str):
    """
    Download the markdown report.

    Args:
        analysis_id: Analysis ID

    Returns:
        Markdown file download
    """
    report_path = f"analyses/{analysis_id}/report.md"

    if not os.path.exists(report_path):
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    return FileResponse(
        report_path,
        media_type="text/markdown",
        filename=f"github_analysis_{analysis_id[:8]}.md"
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "github-analyzer"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
