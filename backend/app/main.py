from fastapi import FastAPI
from datetime import datetime,timezone
from typing import Any
from fastapi import HTTPException
from fastapi import Response
import random   
from pydantic import BaseModel
from sqlalchemy import create_engine ,select,Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi import Depends
from typing import Annotated
from contextlib import asynccontextmanager


Base = declarative_base()


class Campaign(Base):
    __tablename__ = "campaigns"

    campaign_id = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String, nullable=False, index=True)
    due_date    = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at  = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

DATABASE_URL = "sqlite:///database.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SessionDep = Annotated[Session, Depends(get_db)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        if not session.execute(select(Campaign)).scalars().first():  
            session.add_all([
                Campaign(name="Summer Launch", due_date=datetime.now(timezone.utc)),
                Campaign(name="Black Friday", due_date=datetime.now(timezone.utc))
            ])
            session.commit()
    yield

app = FastAPI(root_path="/api/v1",lifespan=lifespan)


class CampaignRead(BaseModel):
    campaign_id: int
    name: str
    due_date: datetime | None
    created_at: datetime | None

    model_config = {"from_attributes": True}


class CampaignCreate(BaseModel):
    name: str
    due_date: datetime | None = None


@app.get("/campaigns", response_model=list[CampaignRead])
async def read_campaign(db: SessionDep):
    data = db.execute(select(Campaign)).scalars().all()
    return data


@app.get("/campaigns/{id}", response_model=CampaignRead)
async def get_campaign(id: int, db: SessionDep):
    data = db.get(Campaign,id)
    if not data:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return data



@app.post("/campaigns", response_model=CampaignRead, status_code=201)
async def create_campaign(body: CampaignCreate, db: SessionDep):
    new = Campaign(
        name=body.name,
        due_date=body.due_date
    )
    db.add(new)
    db.commit()
    db.refresh(new)
    return new




@app.put("/campaign",status_code=200,response_model=CampaignRead)
async def update_campaign(id: int,body: CampaignCreate,db:SessionDep):
    data = db.get(Campaign,id) 
    if not data:
        raise HTTPException(status_code=404) 
    data.name = body.name
    data.due_date = body.due_date
    db.commit()
    db.refresh(data)
    return data


@app.delete("/campaign",status_code=204)
async def delete_campaign(id: int,db:SessionDep):
    data=db.get(Campaign,id)
    if not data:
        raise HTTPException(status_code=404)
    db.delete(data)
    db.commit()
    return Response(status_code=204)
