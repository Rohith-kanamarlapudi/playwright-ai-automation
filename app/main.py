from fastapi import FastAPI, Request, UploadFile, File, Header, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from agents.pipeline import run_agent_pipeline
from agents.doc_sanitiser import sanitise_document
import asyncio


import os

from app.llm_generator import generate_test_cases
from app.yaml_validator import validate_yaml
from app.yaml_to_playwright import convert_yaml_to_playwright

APP_API_KEY = os.getenv("APP_API_KEY", "")   # set in .env for production

def verify_api_key(x_api_key: str = Header(default="")):
    """
    Require X-API-Key header on protected endpoints.
    Skip check if APP_API_KEY is not configured (dev mode).
    """
    if APP_API_KEY and x_api_key != APP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key header.")
    

app = FastAPI(title="Test Case Generator")

class PipelineRequest(BaseModel):
    design_doc: str
    target_url: str | None = None

# -------------------------------------
# Create folders if missing
# -------------------------------------

os.makedirs("uploads", exist_ok=True)
os.makedirs("output", exist_ok=True)

# -------------------------------------
# Templates
# -------------------------------------

templates = Jinja2Templates(
    directory="app/templates"
)

# -------------------------------------
# Static Files
# -------------------------------------

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)


# -------------------------------------
# Home Page
# -------------------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request
        }
    )


# -------------------------------------
# Upload Route
# -------------------------------------

@app.post("/upload", response_class=HTMLResponse)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    _: None = Depends(verify_api_key),
):

    try:

        # ----------------------------
        # Validate File
        # ----------------------------

        if not file.filename:

            return templates.TemplateResponse(
                request=request,
                name="results.html",
                context={
                    "request": request,
                    "error": "No file selected."
                }
            )

        allowed_extensions = [
            ".txt",
            ".md",
            ".pdf"
        ]

        extension = os.path.splitext(
            file.filename
        )[1].lower()

        if extension not in allowed_extensions:

            return templates.TemplateResponse(
                request=request,
                name="results.html",
                context={
                    "request": request,
                    "error": f"Unsupported file type: {extension}"
                }
            )

        # ----------------------------
        # Save Uploaded File
        # ----------------------------

        from pathlib import Path
        safe_name = Path(file.filename).name
        file_path = os.path.join("uploads", safe_name)

        content = await file.read()

        with open(
            file_path,
            "wb"
        ) as f:

            f.write(content)

        print("File saved:", file_path)

        # ----------------------------
        # Read Document Content
        # ----------------------------

        document_text = ""

        if extension == ".pdf":

            from pypdf import PdfReader

            with open(file_path, "rb") as pdf_file:
                reader = PdfReader(pdf_file)


                for page in reader.pages:

                    page_text = page.extract_text()

                    if page_text:
                        document_text += page_text

        else:

            document_text = content.decode(
                "utf-8",
                errors="ignore"
            )

        document_text, warnings = sanitise_document(document_text)
        
        if not document_text.strip():
            raise ValueError("Uploaded document contains no readable text.")

        if warnings:
            print(f"[Security] Document sanitised. Warnings: {warnings}")

        print("\n========== DOCUMENT ==========")
        print(document_text[:500])
        print("==============================\n")




        # ----------------------------
        # Authoritative path: LangGraph Agent Pipeline
        # ----------------------------
        agent_result = await asyncio.to_thread(
            run_agent_pipeline,
            design_doc=document_text,
        )

        # Use the agent pipeline's generated YAML as the primary output
        yaml_output = agent_result.get("generated_yaml", "")
        if not yaml_output.strip():
            yaml_output = generate_test_cases(document_text)

        # Fallback: only call llm_generator if the pipeline produced nothing
        if not yaml_output.strip():
            print("[Upload] Agent pipeline returned no YAML — falling back to llm_generator.")
            yaml_output = generate_test_cases(document_text)
        print("\n========== YAML OUTPUT ==========")
        print(yaml_output)
        print("=================================\n")

        # ----------------------------
        # Validate YAML
        # ----------------------------

        validation = validate_yaml(
            yaml_output
        )

        print("Validation Result:")
        print(validation)

        # ----------------------------
        # Convert to Playwright
        # ----------------------------

        playwright_output = convert_yaml_to_playwright(
            yaml_output
        )

        print("Playwright Conversion Complete")

        # ----------------------------
        # Render Results Page
        # ----------------------------

        return templates.TemplateResponse(
            request=request,
            name="results.html",
            context={
                "request": request,
                "filename": file.filename,
                "preview": document_text[:1500],

                # Existing outputs
                "yaml_output": yaml_output,
                "validation": validation,
                "playwright_output": playwright_output.get(
                    "code",
                    "No Playwright code generated"
                ),
                "test_cases": playwright_output.get(
                    "test_cases",
                    []
                ),

                # LangGraph outputs
                "agent_task_plan": agent_result.get("task_plan", []),
                "agent_code": agent_result.get("generated_code", ""),
                "agent_review": agent_result.get("review_notes", ""),
                "agent_edge_cases": agent_result.get("edge_cases", []),
                "agent_architecture": agent_result.get("architecture_notes", "")
            }
        )

    except Exception as e:

        print("\n========== ERROR ==========")
        print(str(e))
        print("===========================\n")

        return templates.TemplateResponse(
            request=request,
            name="results.html",
            context={
                "request": request,
                "error": str(e)
            }
        )
# -------------------------------------
# LangGraph Agent Pipeline API
# -------------------------------------

@app.post("/agents/run")
async def run_agents(req: PipelineRequest, _: None = Depends(verify_api_key)):
    """
    Runs the complete LangGraph Agent Pipeline.
    """

    try:

        result = await asyncio.to_thread(
            run_agent_pipeline,
            design_doc=req.design_doc,
            target_url=req.target_url
            )

        return {
            "status": "success",
            "task_plan": result.get("task_plan", []),
            "architecture_notes": result.get("architecture_notes", ""),
            "generated_code": result.get("generated_code", ""),
            "review_notes": result.get("review_notes", ""),
            "edge_cases": result.get("edge_cases", []),
            "selectors": result.get("selectors", [])
        }

    except Exception as e:

        print("\n========== AGENT PIPELINE ERROR ==========")
        print(str(e))
        print("==========================================\n")

        return {
            "status": "error",
            "message": str(e)
        }