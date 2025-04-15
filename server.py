# server.py
from mcp.server.fastmcp import FastMCP
import requests
import json
import os
from starlette.applications import Starlette
from starlette.routing import Mount, Host
from geopy.geocoders import Nominatim
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create an MCP server
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
def get_lat_lan(place: str) -> json:
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
def get_weather(latitude: float, longitude: float) -> json:
    '''
    根據經緯度搜尋天氣預報

    Args:
        lat (float): 緯度
        lon (float): 經度

    Returns:
        json
    '''
    
    # 使用openweather的API密鑰
    base_url = 'https://api.openweathermap.org/data/2.5/weather'
    API_KEY = os.getenv('OPENWEATHER_API_KEY')
    
    params = {
        'lat': latitude,
        'lon': longitude,
        'appid': API_KEY,   # 使用openweather的API密鑰
        'units': 'metric',  # 使用攝氏溫度
        'lang': 'zh_tw'     # 使用繁體中文
    }
    
    try:
        response = requests.get(base_url, params=params)
        # 檢查請求是否成功
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}


# stdio傳輸格式選擇下方本地server配置文件
# sse傳輸格式 選擇下方sse配置文件
if __name__ == "__main__":
    print("Starting MCP server...")
    print(get_lat_lan("台北101"))
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