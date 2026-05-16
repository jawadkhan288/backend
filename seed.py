"""
seed.py — Seed the Supabase PostgreSQL database with the 8 initial sample candidates
from the original SharedContext.tsx hardcoded data.

Run once after migrations:
    python seed.py
"""
import asyncio
from datetime import date

from database import AsyncSessionLocal
from models import Candidate, CandidateStatus


SAMPLE_CANDIDATES = [
    {
        "name": "Alexander Smith",
        "email": "alex.smith@email.com",
        "phone": "+1 (555) 123-4567",
        "position": "Senior Frontend Developer",
        "ai_score": 94,
        "experience": "8 years",
        "skills": ["React", "TypeScript", "Node.js"],
        "status": CandidateStatus.Interview,
        "avatar": "https://i.pravatar.cc/150?img=33",
        "applied_date": date(2024, 2, 20),
        "match_reasons": ["8+ years experience", "Expert in React & TypeScript", "Leadership experience"],
    },
    {
        "name": "Marcus Johnson",
        "email": "marcus.j@email.com",
        "phone": "+1 (555) 234-5678",
        "position": "Product Manager",
        "ai_score": 88,
        "experience": "6 years",
        "skills": ["Product Strategy", "Agile", "Data Analysis"],
        "status": CandidateStatus.Screened,
        "avatar": "https://i.pravatar.cc/150?img=11",
        "applied_date": date(2024, 2, 19),
        "match_reasons": ["Strong product background", "Agile certification", "Data-driven approach"],
    },
    {
        "name": "Steven Chen",
        "email": "steven.c@email.com",
        "phone": "+1 (555) 345-6789",
        "position": "UX/UI Designer",
        "ai_score": 92,
        "experience": "5 years",
        "skills": ["Figma", "User Research", "Prototyping"],
        "status": CandidateStatus.Offer,
        "avatar": "https://i.pravatar.cc/150?img=51",
        "applied_date": date(2024, 2, 18),
        "match_reasons": ["Portfolio excellence", "User-centered design", "5+ years experience"],
    },
    {
        "name": "James Williams",
        "email": "james.w@email.com",
        "phone": "+1 (555) 456-7890",
        "position": "Backend Developer",
        "ai_score": 85,
        "experience": "7 years",
        "skills": ["Python", "Django", "PostgreSQL"],
        "status": CandidateStatus.Applied,
        "avatar": "https://i.pravatar.cc/150?img=13",
        "applied_date": date(2024, 2, 21),
        "match_reasons": ["Strong backend skills", "Database expertise", "Scalable architecture"],
    },
    {
        "name": "Ethan Davis",
        "email": "ethan.d@email.com",
        "phone": "+1 (555) 567-8901",
        "position": "Data Analyst",
        "ai_score": 90,
        "experience": "4 years",
        "skills": ["SQL", "Python", "Tableau"],
        "status": CandidateStatus.Hired,
        "avatar": "https://i.pravatar.cc/150?img=52",
        "applied_date": date(2024, 2, 10),
        "match_reasons": ["Advanced analytics", "Visualization expert", "Business insights"],
    },
    {
        "name": "Robert Martinez",
        "email": "robert.m@email.com",
        "phone": "+1 (555) 678-9012",
        "position": "DevOps Engineer",
        "ai_score": 87,
        "experience": "6 years",
        "skills": ["AWS", "Docker", "Kubernetes"],
        "status": CandidateStatus.Interview,
        "avatar": "https://i.pravatar.cc/150?img=14",
        "applied_date": date(2024, 2, 17),
        "match_reasons": ["Cloud expertise", "CI/CD mastery", "Infrastructure automation"],
    },
    {
        "name": "Liam Anderson",
        "email": "liam.a@email.com",
        "phone": "+1 (555) 789-0123",
        "position": "Senior Frontend Developer",
        "ai_score": 78,
        "experience": "3 years",
        "skills": ["React", "JavaScript", "CSS"],
        "status": CandidateStatus.Screened,
        "avatar": "https://i.pravatar.cc/150?img=53",
        "applied_date": date(2024, 2, 22),
        "match_reasons": ["Modern framework skills", "Growing portfolio", "Team player"],
    },
    {
        "name": "Daniel Brown",
        "email": "daniel.b@email.com",
        "phone": "+1 (555) 890-1234",
        "position": "Product Manager",
        "ai_score": 82,
        "experience": "5 years",
        "skills": ["Product Management", "Roadmapping", "Analytics"],
        "status": CandidateStatus.Applied,
        "avatar": "https://i.pravatar.cc/150?img=16",
        "applied_date": date(2024, 2, 23),
        "match_reasons": ["Strategic thinking", "Cross-functional lead", "User focus"],
    },
]


async def seed():
    print("🌱 Seeding database with sample candidates...")
    async with AsyncSessionLocal() as session:
        for data in SAMPLE_CANDIDATES:
            candidate = Candidate(**data)
            session.add(candidate)
        await session.commit()
    print(f"✅ Seeded {len(SAMPLE_CANDIDATES)} candidates successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
