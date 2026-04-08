
from .otp_router import router as otp_router
from .route_router import router as route_router
from .poi_router import router as poi_router
from .geocode_router import router as geocode_router
from .contribution_router import router as contribution_router
from .contributions_router import router as contributions_router
from .user_router import router as user_router
from .admin_router import router as admin_router
from .admin_user_router import router as admin_user_router
from .health import router as health_router
from .admin_business_router import router as admin_business_router
from .contribution_group_router import router as contribution_group_router
from .service_provider_router import router as service_provider_router


all_routers = [
    {"router": health_router, "prefix": ""},
    {"router": route_router, "prefix": ""},
    {"router": poi_router, "prefix": ""},
    {"router": geocode_router, "prefix": ""},
    {"router": contribution_router, "prefix": ""},
    {"router": contributions_router, "prefix": ""},
    {"router": user_router, "prefix": "/api"},
    {"router": admin_router, "prefix": ""},
    {"router": admin_user_router, "prefix": ""},
    {"router": admin_business_router, "prefix": ""},
    {"router": otp_router, "prefix": ""},
    {"router": contribution_group_router, "prefix": ""},
    {"router": service_provider_router, "prefix": ""}

    
]