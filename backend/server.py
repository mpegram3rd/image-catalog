import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP

from api import image_catalog_router
from mcp_tools.image_catalog_mcp import image_catalog_mcp

# Prepare MCP
mcp = FastMCP("CompositeServer")
mcp_app = mcp.http_app(path='/mcp')

# Prepare APIs
app = FastAPI(title="Image Catalog Tools API", lifespan=mcp_app.lifespan)
app.include_router(image_catalog_router.router)

origins = [
    "http://localhost",
    "http://localhost:5173",
]

# Enable CORS for all origins (DEVELOPMENT ONLY - NOT RECOMMENDED FOR PRODUCTION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach MCP to API server
app.mount("/ai", mcp_app)

# Import subserver
async def setup():
    await mcp.import_server(image_catalog_mcp, "image-catalog")

if __name__ == "__main__":
    asyncio.run(setup())
    uvicorn.run(app, host="0.0.0.0", port=8000, ws="websockets-sansio")