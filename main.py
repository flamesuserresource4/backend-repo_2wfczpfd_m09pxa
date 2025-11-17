import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import create_document, get_documents

app = FastAPI(title="SpellsToGetMyExBack API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!",
            "service": "SpellsToGetMyExBack API"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


# Schemas for responses (simple, for docs)
class TestimonialOut(BaseModel):
    name: str
    location: Optional[str] = None
    message: str
    rating: Optional[int] = 5
    service: Optional[str] = None
    featured: bool = False

class BlogSummary(BaseModel):
    title: str
    slug: str
    excerpt: Optional[str] = None
    tags: List[str] = []
    published: bool = True

class BlogDetail(BlogSummary):
    content: str

class LeadIn(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    message: Optional[str] = None
    source: Optional[str] = "website"
    service_interest: Optional[str] = None


@app.get("/api/testimonials", response_model=List[TestimonialOut])
def list_testimonials(featured: bool = False, limit: int = 12):
    try:
        filter_dict = {"featured": True} if featured else {}
        docs = get_documents("testimonial", filter_dict, limit)
        # convert ObjectId to str-safe dicts
        results = []
        for d in docs:
            d.pop("_id", None)
            results.append(d)
        return results
    except Exception as e:
        # If DB not configured, return a small static sample for graceful UX
        sample = [
            {
                "name": "Sasha",
                "location": "Austin, TX",
                "message": "In my darkest hour, guidance helped me find peace and reunite with my partner.",
                "rating": 5,
                "service": "get-your-ex-back-spell",
                "featured": True,
            }
        ]
        return sample if featured else sample


@app.get("/api/blog", response_model=List[BlogSummary])
def list_blog(limit: int = 15):
    try:
        docs = get_documents("blogpost", {"published": True}, limit)
        results = []
        for d in docs:
            results.append({
                "title": d.get("title"),
                "slug": d.get("slug"),
                "excerpt": d.get("excerpt"),
                "tags": d.get("tags", []),
                "published": d.get("published", True)
            })
        return results
    except Exception:
        # graceful fallback
        return [
            {
                "title": "Understanding Ethical Love Work: A Practical Guide",
                "slug": "ethical-love-work-guide",
                "excerpt": "How to approach reconciliation with compassion, clarity, and respect for free will.",
                "tags": ["ethics", "love", "guides"],
                "published": True,
            }
        ]


@app.get("/api/blog/{slug}", response_model=BlogDetail)
def get_blog(slug: str):
    try:
        docs = get_documents("blogpost", {"slug": slug, "published": True}, 1)
        if not docs:
            raise HTTPException(status_code=404, detail="Post not found")
        d = docs[0]
        return {
            "title": d.get("title"),
            "slug": d.get("slug"),
            "excerpt": d.get("excerpt"),
            "tags": d.get("tags", []),
            "published": d.get("published", True),
            "content": d.get("content", "")
        }
    except HTTPException:
        raise
    except Exception:
        # fallback sample
        if slug == "ethical-love-work-guide":
            return {
                "title": "Understanding Ethical Love Work: A Practical Guide",
                "slug": slug,
                "excerpt": "How to approach reconciliation with compassion and respect.",
                "tags": ["ethics", "love"],
                "published": True,
                "content": "I have helped many over the years navigate matters of the heart with dignity...",
            }
        raise HTTPException(status_code=404, detail="Post not found")


@app.post("/api/leads")
def create_lead(lead: LeadIn):
    try:
        lead_id = create_document("lead", lead.model_dump())
        return {"ok": True, "id": lead_id}
    except Exception as e:
        # still acknowledge receipt even if DB not set, to allow demo
        return {"ok": True, "id": "demo", "note": "stored in memory fallback unavailable; DB not configured"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
