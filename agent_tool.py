import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool
# 确保加载环境变量（通常在文件顶部已有）
load_dotenv()
api_key = os.getenv("QWEATHER_API_KEY")
 # 从环境变量获取专属域名
api_host = os.getenv("QWEATHER_API_HOST")
api_header = {
        'X-QW-Api-Key': api_key,
        'Accept-Encoding': 'gzip'}

@tool
def get_weather(city: str, days: int = 1) -> str:
    """查询城市天气预报。city是城市名，days是天数，默认为1（当天）。"""
    if not api_host:
        return "天气服务未配置，请设置QWEATHER_API_HOST环境变量。"
    if not api_key:
        return "天气服务未配置，请设置QWEATHER_API_API_KEY环境变量。"

    try:
        # 1. 通过城市名获取位置ID
        geo_url =f"https://{api_host}/geo/v2/city/lookup?location={city}"
        # 发送请求时传入 headers
        geo_resp = requests.get(geo_url, headers=api_header).json()

        if geo_resp['code'] != '200' or not geo_resp.get('location'):
            return f"找不到城市‘{city}’，请检查名称是否正确。"

        location_id = geo_resp['location'][0]['id']
        city_name = geo_resp['location'][0]['name']  # 获取标准名称，如“北京市”

        # 2. 根据天数决定调用实时天气（now）还是天气预报（3d/7d）
        if days == 1:
            # 获取实时天气
            weather_url = f"https://{api_host}/v7/weather/now?location={location_id}"
            weather_key = 'now'
        else:
            # 获取多日预报，API最多返回7天
            weather_url = f"https://{api_host}/v7/weather/{days}d?location={location_id}"
            weather_key = 'daily'

        weather_resp = requests.get(weather_url, headers=api_header).json()

        if weather_resp['code'] != '200':
            return f"获取{city_name}的天气数据失败，请稍后再试。"

        # 3. 解析并返回结果
        if days == 1:
            now = weather_resp[weather_key]
            return f"{city_name}当前天气：{now['text']}，温度{now['temp']}℃，体感温度{now['feelsLike']}℃，湿度{now['humidity']}%，风向{now['windDir']}，风力{now['windScale']}级。"
        else:
            forecast_list = weather_resp[weather_key]
            # 只取前 `days` 天的预报
            summary = []
            for day_forecast in forecast_list[:days]:
                date = day_forecast['fxDate']
                day_text = day_forecast['textDay']
                night_text = day_forecast['textNight']
                temp_min = day_forecast['tempMin']
                temp_max = day_forecast['tempMax']
                summary.append(f"{date}: 白天{day_text}，夜间{night_text}，气温{temp_min}~{temp_max}℃")
            return f"{city_name}未来{days}天预报：\n" + "\n".join(summary)

    except requests.exceptions.RequestException as e:
        return f"网络请求出错，无法获取天气：{e}"
    except Exception as e:
        return f"处理天气数据时出现未知错误：{e}"


@tool
def get_air_quality(city: str, days: int = 1) -> str:
    """查询指定城市的实时空气质量指数（AQI）及相关污染物浓度。"""
    if not api_host:
        return "天气服务未配置，请设置QWEATHER_API_HOST环境变量。"
    if not api_key:
        return "天气服务未配置，请设置QWEATHER_API_API_KEY环境变量。"
    try:
        geo_url = f"https://{api_host}/geo/v2/city/lookup?location={city}"
        geo_resp = requests.get(geo_url, headers=api_header).json()

        location_info = geo_resp['location'][0]
        city_name = location_info['name']
        lat = location_info['lat']
        lon = location_info['lon']
        # 构建空气质量预报请求URL，使用经纬度作为路径参数
        aqi_forecast_url = f"https://{api_host}/airquality/v1/daily/{lat}/{lon}"
        aqi_resp = requests.get(aqi_forecast_url, headers=api_header).json()
        print(aqi_resp)
        # 3. 解析返回的JSON数据 (数据结构较复杂)[citation:1]
        days_data = aqi_resp.get('days', [])
        if not days_data:
            return f"未找到{city}的空气质量预报数据。"

        # 根据请求的天数获取数据，注意免费版可能只返回3天[citation:6]
        target_day = days_data[days - 1] if len(days_data) >= days else days_data[0]

        # 实际数据中包含 `qaqi`, `eu-eea` 等多种指数，您可以根据需要选择
        primary_index = target_day['indexes'][0] if target_day.get('indexes') else {}
        aqi_value = primary_index.get('aqiDisplay', 'N/A')
        aqi_category = primary_index.get('category', 'N/A')
        # 翻译类别为中文（简单示例，可按需扩充）
        category_cn = {
            "Excellent": "优", "Good": "良", "Fair": "轻度污染",
            "Poor": "中度污染", "Very Poor": "重度污染", "Severe": "严重污染"
        }.get(aqi_category, aqi_category)

        # 5. 提取健康建议
        health_advice = primary_index.get('health', {}).get('advice', {})
        general_advice = health_advice.get('generalPopulation', '暂无具体建议。')

        # 6. 组织回复
        return f"{city_name}第{days}天空气质量预报：指数 {aqi_value}，等级「{category_cn}」。健康建议：{general_advice}"
                
    except requests.exceptions.RequestException as e:
        return f"网络请求出错：{e}"
    except Exception as e:
        return f"处理空气质量数据时出错：{e}"
