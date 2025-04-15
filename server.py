# server.py
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
import requests
import json
import os
from starlette.applications import Starlette
from starlette.routing import Mount, Host
from geopy.geocoders import Nominatim
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create an MCP server with schemas
mcp = FastMCP("Weather_MCP", log_level="WARNING")


# 靜態資源
@mcp.resource(
    uri="greeting://{name}",
    name='greeting',
    description='根據用戶的名稱打招呼'
)
def get_greeting(name: str) -> str:
    # 訪問 greeting://{name}
    return f"Hello, {name}!"


# Lat_Lan_Tools
@mcp.tool(
    name="Lat_Lan_Tools",
    description="根據地名搜尋經緯度",
)
def get_lat_lan(place: str = Field(..., description="地名，例如 台北烘爐地")) -> dict:
    geolocator = Nominatim(user_agent="my-geopy-app")
    location = geolocator.geocode(place, timeout=5)

    if location is None:
        return {"error": f"找不到地點：{place}"}

    return {
        "latitude": location.latitude,
        "longitude": location.longitude
    }

# Weather_Tools
@mcp.tool(
    name="Weather_Tools",
    description="根據經緯度搜尋天氣預報",
)

def get_weather(latitude: float = Field(..., description="緯度，例如 25.033"), longitude: float = Field(..., description="經度，例如 121.5654")) -> json:   
    # 使用openweather的API密鑰
    base_url = 'https://api.openweathermap.org/data/2.5/weather'
    API_KEY = os.getenv('OPENWEATHER_API_KEY')
    
    query = {
        'lat': latitude,
        'lon': longitude,
        'appid': API_KEY,
        'units': 'metric',
        'lang': 'zh_tw'
    }
    
    try:
        response = requests.get(base_url, params=query)
        # 檢查請求是否成功
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}


# stdio傳輸格式選擇下方本地server配置文件
# sse傳輸格式 選擇下方sse配置文件
if __name__ == "__main__":
    print("Starting MCP server...")
    mcp.run(transport="sse")



# 用 starlette 掛 mcp 的 HTTP app
# uvicorn server:app --host 0.0.0.0 --port 8000
'''
# 用 starlette 掛 mcp 的 SSE app
app = Starlette(
    routes=[
        Mount('/', app = mcp.sse_app()),
    ]
)
'''