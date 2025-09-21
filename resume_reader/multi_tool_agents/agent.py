import os
import json
import asyncio
from google.adk.agents import Agent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

# Step 1: In-memory artifact storage
artifact_service = InMemoryArtifactService()
session_service = InMemorySessionService()
# Step 2: Tool for uploading resume PDF
async def upload_resume(file_path: str) -> dict:
    """Uploads a resume PDF into the in-memory artifact store."""
    if not os.path.exists(file_path):
        return {"status": "error", "error_message": f"File not found: {file_path}"}

    try:
        with open(file_path, "rb") as f:
            pdf_data = f.read()

        file_part = types.Part.from_bytes(pdf_data, mime_type="application/pdf")
        filename = os.path.basename(file_path)

        version = await artifact_service.save_artifact(filename, file_part)

        return {
            "status": "success",
            "artifact": {"filename": filename, "version": version},
        }

    except Exception as e:
        return {"status": "error", "error_message": str(e)}

# Step 3: Define Agent
root_agent = Agent(
    name="resume_qa_agent",
    model="gemini-2.0-flash",
    description="Agent that extracts at least 20 Questions and Answers from a resume PDF",
    instruction=(
        "You are a helpful assistant. Read the uploaded resume PDF artifact "
        "and generate **at least 20 interview-style questions with answers** "
        "extracted from the resume content. "
        "Output only valid JSON in the format:\n\n"
        "{\n  \"questions\": [\n    {\"question\": \"...\", \"answer\": \"...\"},\n    ...\n  ]\n}"
    ),
    tools=[upload_resume],
)

# Step 4: Runner to execute agent
runner = Runner(app_name="resume_qna_app",agent=root_agent, artifact_service=artifact_service,session_service=session_service)

# Step 5: Process resume and download JSON
async def process_resume(file_path: str, output_json: str = "resume_qna.json"):
    # Upload the resume
    upload_result = await upload_resume(file_path)
    if upload_result["status"] == "error":
        return upload_result

    artifact_ref = upload_result["artifact"]

    # Ask the agent to extract Q&A
    response = await runner.run(
        input=[
            types.Part.from_text(
                f"Please extract at least 20 questions and answers from the resume artifact '{artifact_ref['filename']}'."
            )
        ]
    )

    # Agent's JSON output
    qna_text = response.output_text.strip()
    print("QnA",qna_text)
    try:
        qna_json = json.loads(qna_text)  # ensure valid JSON
        print("JSON",qna_json)
    except Exception:
        # Fallback: wrap raw text if JSON parsing fails
        qna_json = {"questions": [], "raw_output": qna_text}

    # Save JSON file (downloadable)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(qna_json, f, indent=2, ensure_ascii=False)

    return {
        "status": "success",
        "message": f"Extracted Q&A saved to {output_json}",
        "file": output_json,
    }


# Example usage
# asyncio.run(process_resume("resume.pdf", "resume_qna.json"))
