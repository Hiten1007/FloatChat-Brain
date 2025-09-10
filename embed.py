import csv
import os
import dotenv
import numpy as np
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

dotenv.load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

# Connect to existing index
index_name = "argo-floats-india"
index = pc.Index(index_name)

# Load CPU/GPU-friendly local embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')  # 384-dimensional, fast on CPU

# Fixed column order (40 fields)
FIELDS = [
    "DATA_TYPE","FORMAT_VERSION","HANDBOOK_VERSION","DATE_CREATION","DATE_UPDATE",
    "PLATFORM_NUMBER","PROJECT_NAME","PI_NAME","CYCLE_NUMBER","DIRECTION",
    "DATA_CENTRE","DATA_STATE_INDICATOR","DATA_MODE","PLATFORM_TYPE","FLOAT_SERIAL_NO",
    "FIRMWARE_VERSION","WMO_INST_TYPE","JULD","JULD_LOCATION","LATITUDE",
    "LONGITUDE","POSITIONING_SYSTEM","PROFILE_PRES_QC","PROFILE_TEMP_QC","PROFILE_PSAL_QC",
    "VERTICAL_SAMPLING_SCHEME","CONFIG_MISSION_NUMBER","PARAMETER",
    "SCIENTIFIC_CALIB_EQUATION","SCIENTIFIC_CALIB_COMMENT","SCIENTIFIC_CALIB_DATE",
    "HISTORY_INSTITUTION","HISTORY_STEP","HISTORY_SOFTWARE","HISTORY_SOFTWARE_RELEASE",
    "HISTORY_REFERENCE","HISTORY_DATE","HISTORY_ACTION","HISTORY_PARAMETER","HISTORY_QCTEST"
]

def row_to_text(row: dict) -> str:
    """Convert a CSV row into descriptive string with fixed field order."""
    lines = []
    for field in FIELDS:
        value = row.get(field, "").strip()
        if not value:
            value = "N/A"
        lines.append(f"{field}: {value}")
    return "\n".join(lines)

def embed_and_store(row: dict, row_id: str):
    """Generate embeddings locally and store in Pinecone."""
    record_text = row_to_text(row)

    # Local embedding
    embedding = model.encode(record_text)
    embedding = embedding.tolist()  # Convert to list for Pinecone

    # Metadata
    metadata = {field: (row.get(field, "").strip() or "N/A") for field in FIELDS}

    # Store in Pinecone
    index.upsert([
        {
            "id": row_id,
            "values": embedding,
            "metadata": metadata
        }
    ])
    print(f"Stored row {row_id} in Pinecone.")

# Load CSV and push to Pinecone in batches
with open("cleaned_metadata[1].csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i <= 75105:
            continue  # skip rows already stored
        embed_and_store(row, row_id=f"record-{i}")
