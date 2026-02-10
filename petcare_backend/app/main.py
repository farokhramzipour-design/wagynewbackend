from fastapi import FastAPI

from app.core.logging import setup_logging
from app.api.v1.routers import auth as auth_router
from app.api.v1.routers import admin as admin_router
from app.api.v1.routers import availability as availability_router
from app.api.v1.routers import bookings as bookings_router
from app.api.v1.routers import geo as geo_router
from app.api.v1.routers import meet_greets as meet_greets_router
from app.api.v1.routers import messaging as messaging_router
from app.api.v1.routers import media as media_router
from app.api.v1.routers import onboarding as onboarding_router
from app.api.v1.routers import providers as providers_router
from app.api.v1.routers import payments as payments_router
from app.api.v1.routers import pets as pets_router
from app.api.v1.routers import charity as charity_router
from app.api.v1.routers import reviews as reviews_router
from app.api.v1.routers import search as search_router
from app.api.v1.routers import users as users_router
from app.api.v1.routers import wallets as wallets_router


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="Pet Care Marketplace")
    app.include_router(auth_router.router)
    app.include_router(admin_router.router)
    app.include_router(availability_router.router)
    app.include_router(bookings_router.router)
    app.include_router(geo_router.router)
    app.include_router(meet_greets_router.router)
    app.include_router(messaging_router.router)
    app.include_router(media_router.router)
    app.include_router(onboarding_router.router)
    app.include_router(payments_router.router)
    app.include_router(pets_router.router)
    app.include_router(providers_router.router)
    app.include_router(charity_router.router)
    app.include_router(reviews_router.router)
    app.include_router(search_router.router)
    app.include_router(users_router.router)
    app.include_router(wallets_router.router)
    return app


app = create_app()
