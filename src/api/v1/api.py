from fastapi import APIRouter

from src.api.v1 import (
    auth,
    prices,
    transaction,
    profile,
    dashboard,
    wallet,
    partner,
    payment,
    admin,
)

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router, prefix="/auth/v1")
api_router.include_router(prices.router, prefix="/data/v1")
api_router.include_router(dashboard.router, prefix="/dashboard/v1")
api_router.include_router(transaction.router, prefix="/transaction/v1")
api_router.include_router(wallet.router, prefix="/wallet/v1")
api_router.include_router(profile.router, prefix="/profile/v1")
api_router.include_router(partner.router, prefix="/partner/v1")
api_router.include_router(payment.router, prefix="/payment/v1")
api_router.include_router(admin.router, prefix="/admin/v1")
