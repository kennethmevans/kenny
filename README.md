# Backend Server Overview  
*(Django REST + PostgreSQL + Elasticsearch)*

This backend is a pure **Django REST Framework (DRF)** service—no LLM or other AI components are included in the current release.

| Component | Technology | Purpose | Deployment Location |
|-----------|------------|---------|---------------------|
| **Relational DB** | **PostgreSQL** | Stores structured data for `Person`, `Institution`, `Document`, table metadata, and named-entity tables | **RICE CRC remote cluster** |
| **Search Engine** | **Elasticsearch** | Holds full-text content of documents and provides fuzzy / substring search | **Local workstation** (not on CRC yet) |

## Configuration Notes

| Version | What’s required to run |
|---------|------------------------|
| **v1 (SQL only)** | PostgreSQL is already deployed on CRC. Copy the provided `.env` file (contains DB credentials) and start the server—no other changes needed. |
| **v2 (SQL + Elasticsearch)** | Keep the CRC PostgreSQL settings **and** edit `PCAST_django/PCAST_django/settings.py` to match your ES instance (`hosts`, `http_auth`, SSL flags). Without a valid ES connection, v2 will raise startup errors. |

---

## 1 Relational Database (PostgreSQL on CRC)

| Topic | Details |
|-------|---------|
| **Purpose** | Stores all structured metadata—`Person`, `Institution`, `Document`, plus supporting tables (e.g., file-level metadata, named-entity counts). |
| **Deployment** | PostgreSQL cluster managed by the university’s CRC. Connection parameters (host, port, user, password, DB name) are injected via a project-level `.env` file. |
| **API Coverage** | *Persons* `GET/POST/PUT/PATCH/DELETE /api/persons/`<br>*Institutions* `GET/POST/PUT/PATCH/DELETE /api/institution/`<br>*Documents* `GET/POST/PUT/PATCH/DELETE /api/doc/`<br>All endpoints are generated with DRF ViewSets and exchange JSON. |
| **Admin Interface** | Django Admin auto-registers every model. Super-users can perform batch inserts/edits, import CSV, run filters, etc.—even for tables that do **not** have public REST endpoints. |
| **Reference Sheet** | An Excel workbook shipped with the repo lists every REST path—**both SQL and Elasticsearch APIs**—along with method and parameter details for quick onboarding. |
| **Version Note – v1** | The original release depended only on this layer; copying `.env` (CRC credentials) and running `python manage.py runserver` is enough for a no-ES setup. |

---

## 2 Elasticsearch Integration (Edge N-Gram Substring Search)

| Topic | Details |
|-------|---------|
| **Local-Only in v2** | ES is currently local; not yet deployed on CRC. All ES host/credential settings live in `PCAST_django/PCAST_django/settings.py`. |
| **Auto Index Creation** | On Django startup (`AppConfig.ready()`):<br>1. Connect to ES.<br>2. If the `documents` index is missing, create it with a custom **`edge_ngram_analyzer`**.<br>3. Mapping:<br>&nbsp;&nbsp;• `title` → `text`<br>&nbsp;&nbsp;• `asset_id` → `keyword`<br>&nbsp;&nbsp;• `full_text` → `text` **plus** `full_text.ngram` (edge-ngram sub-field). |
| **ES Endpoints** | `POST /es_api/create_document/` – add a doc<br>`GET /es_api/list_documents/` – list all docs<br>`GET /es_api/search/?q=term` – substring search via `full_text.ngram`<br>`DELETE /es_api/delete_index/` – drop the index (for rebuilds) |
| **Example Query** | ```bash<br>curl "http://localhost:8001/es_api/search/?q=search"<br>``` returns docs containing *search*, *searchable*, *research*, etc. |
| **Fallback Option** | During testing you may disable the `es_documents` app or comment-out the ES config to run v2 in SQL-only mode. |

---

## Combined Value

* **PostgreSQL** – provides strict relational integrity, foreign-key constraints, and reliable CRUD operations.  
* **Elasticsearch** – delivers high-speed, edge-ngram-based substring search across large document bodies.


## Further Work & Notes

This backend is functional in its current form but includes several components that are either temporarily mocked or awaiting further integration:

1. **Elasticsearch Production Deployment**  
   At this stage, Elasticsearch is only locally deployed for testing purposes. All ES-related document insertions are currently ad hoc and temporary.  
   To support real-world, large-scale full-text search, ES needs to be deployed on the CRC remote server. This will require:  
   - A production ES instance setup  
   - Full-text content retrieval and preprocessing  
   - Batch ingestion of documents into ES via custom scripts or a management command

2. **LLM and Smart Component Integration**  
   The backend is designed to remain compatible with future integration of LLM-based modules (e.g., summarization, entity linking, question answering), but no such interface has yet been implemented. These will be added as separate APIs.

3. **Frontend Connection**  
   The backend currently functions independently without a user interface. Future work includes exposing these APIs to a frontend application, which may consume both SQL and ES data.

4. **RDF Storage Integration**  
   The system is expected to interoperate with the university's RDF storage system. This integration would allow each `Document` record to link to its original source file (e.g., via persistent URI or SPARQL endpoint).

5. **Expanded SQL REST API Coverage**  
   At present, only three SQL models—`Person`, `Institution`, and `Document`—have publicly exposed REST APIs.  
   Many other models exist but are only accessible via Django Admin. As project requirements evolve, more DRF-based APIs may be implemented to allow programmatic access to these tables.
