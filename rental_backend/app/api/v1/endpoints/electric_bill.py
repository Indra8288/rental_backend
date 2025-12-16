from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path
import shutil

from app.db.session import get_db
from app.api.deps import require_roles
from app.models.enums import Role
from app.core.config import settings
from app.models.electric_bill_image import ElectricBillImage

router = APIRouter(prefix="/electric-bill")

@router.post("/upload")
def upload_bill(date_key: str, file: UploadFile = File(...), db: Session = Depends(get_db), _=Depends(require_roles(Role.owner, Role.admin))):
    upload_dir = Path(settings.UPLOAD_DIR) / "electric_bill"
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / f"bill_{date_key}_{file.filename}"
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    rec = ElectricBillImage(date_key=date_key, image_path=str(dest.as_posix()))
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return {"id": rec.id, "date_key": rec.date_key, "image_path": rec.image_path}

@router.get("/{date_key}")
def get_bill(date_key: str, db: Session = Depends(get_db), _=Depends(require_roles(Role.owner, Role.admin))):
    rec = db.query(ElectricBillImage).filter(ElectricBillImage.date_key == date_key).order_by(ElectricBillImage.created_at.desc()).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Bill image not found")
    return {"date_key": date_key, "image_path": rec.image_path}
