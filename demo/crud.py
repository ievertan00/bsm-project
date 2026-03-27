from sqlalchemy.orm import Session
import models

# Bulk create functions
def bulk_create_business_data(db: Session, business_data_list: list[dict]):
    # Filter keys to only include those present in the model
    valid_keys = models.BusinessData.__table__.columns.keys()
    filtered_data = [{k: v for k, v in item.items() if k in valid_keys} for item in business_data_list]
    db.bulk_insert_mappings(models.BusinessData, filtered_data)
    db.commit()


def bulk_create_qcc_industry(db: Session, qcc_industry_list: list[dict]):
    valid_keys = models.QCCIndustry.__table__.columns.keys()
    filtered_data = [{k: v for k, v in item.items() if k in valid_keys} for item in qcc_industry_list]
    db.bulk_insert_mappings(models.QCCIndustry, filtered_data)
    db.commit()


def bulk_create_qcc_tech(db: Session, qcc_tech_list: list[dict]):
    valid_keys = models.QCCTech.__table__.columns.keys()
    filtered_data = [{k: v for k, v in item.items() if k in valid_keys} for item in qcc_tech_list]
    db.bulk_insert_mappings(models.QCCTech, filtered_data)
    db.commit()


def bulk_create_qyjh_list(db: Session, qyjh_list: list[dict]):
    valid_keys = models.QYJHList.__table__.columns.keys()
    filtered_data = [{k: v for k, v in item.items() if k in valid_keys} for item in qyjh_list]
    db.bulk_insert_mappings(models.QYJHList, filtered_data)
    db.commit()


def delete_business_data_by_snapshot(db: Session, year: int, month: int):
    db.query(models.BusinessData).filter(
        models.BusinessData.snapshot_year == year,
        models.BusinessData.snapshot_month == month
    ).delete()
    db.commit()


def clear_qcc_industry(db: Session):
    db.query(models.QCCIndustry).delete()
    db.commit()


def clear_qcc_tech(db: Session):
    db.query(models.QCCTech).delete()
    db.commit()


def clear_qyjh_list(db: Session):
    db.query(models.QYJHList).delete()
    db.commit()



