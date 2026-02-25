import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP

from api_routes import image_catalog_router
from configuration.config import Config
from configuration.logging_config import get_logger, setup_logging
from core.middleware import setup_error_handling, setup_request_logging
from mcp_tools.image_catalog_mcp import image_catalog_mcp

logger = get_logger(__name__)

# Prepare MCP
mcp = FastMCP("CompositeServer")
mcp_app = mcp.http_app(path="/mcp")

# Initialize configuration and logging
config = Config()
setup_logging(
    level=config.log_level,
    json_format=config.log_json_format,
    log_file=config.log_file,
)

# Prepare APIs
app = FastAPI(
    title="Image Catalog Tools API",
    description="AI-powered image search and cataloging API",
    version="1.0.0",
    lifespan=mcp_app.lifespan
)

# Setup middleware (order matters - error handling should be first)
setup_error_handling(app)
setup_request_logging(app)

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:5174",
]

# Note: CORS allows all origins for development - restrict for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(image_catalog_router.router)

# Attach MCP to API server
app.mount("/ai", mcp_app)

logger.info("FastAPI application initialized", extra={
    "cors_origins": origins,
    "mcp_mounted": True,
    "middleware_configured": True,
})


async def setup():
    """Setup MCP server integration."""
    try:
        await mcp.import_server(image_catalog_mcp, "image-catalog")
        logger.info("MCP server integration completed successfully")
    except Exception as e:
        logger.error("Failed to setup MCP server integration", extra={"error": str(e)})
        raise


if __name__ == "__main__":
    try:
        asyncio.run(setup())

        logger.info(
            "Starting server",
            extra={
                "host": config.server_host,
                "port": config.server_port,
                "log_level": config.log_level,
            }
        )

        # Note: Set SERVER_HOST=0.0.0.0 in .env to allow external connections (development only)
        uvicorn.run(
            app,
            host=config.server_host,
            port=config.server_port,
            log_config=None,  # Use our logging configuration
        )

    except Exception as e:
        logger.error("Failed to start server", extra={"error": str(e)})
        raise
