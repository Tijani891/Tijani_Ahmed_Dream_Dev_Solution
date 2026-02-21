from fastapi import APIRouter, HTTPException
from src.app.services import analytics as svc

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/top-merchant")
def top_merchant():
    try:
        return svc.get_top_merchant()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monthly-active-merchants")
def monthly_active_merchants():
    try:
        return svc.get_monthly_active_merchants()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/product-adoption")
def product_adoption():
    try:
        return svc.get_product_adoption()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kyc-funnel")
def kyc_funnel():
    try:
        return svc.get_kyc_funnel()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/failure-rates")
def failure_rates():
    try:
        return svc.get_failure_rates()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))