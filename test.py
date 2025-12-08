import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agent_tool import get_air_quality
import requests


if __name__ == "__main__":
    print(get_air_quality("重庆",1))



def get_air_quality(your_api_host,headers,city_name,latitude,longitude,forecast_days):
    # 构建空气质量预报请求URL，使用经纬度作为路径参数
    aqi_forecast_url = f"https://{your_api_host}/airquality/v1/daily/{latitude}/{longitude}"
    aqi_resp = requests.get(aqi_forecast_url, headers=headers).json()
    print(aqi_resp)
    # 3. 解析返回的JSON数据 (数据结构较复杂)[citation:1]
    days_data = aqi_resp.get('days', [])
    if not days_data:
        return f"未找到{headers}的空气质量预报数据。"

    # 根据请求的天数获取数据，注意免费版可能只返回3天[citation:6]
    target_day = days_data[forecast_days - 1] if len(days_data) >= forecast_days else days_data[0]

    # 4. 提取信息：这里以取第一个指数（例如QAQI）为例[citation:1]
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
    return f"{city_name}第{forecast_days}天空气质量预报：指数 {aqi_value}，等级「{category_cn}」。健康建议：{general_advice}"
def get_weather():
    api_key ="746844dfb5264e8795ba4725ce0769ed"
    # 1. 请在此处替换成您自己的专属域名
    your_api_host = "na4bjaj3yx.re.qweatherapi.com"  # 例如：abc123.qweatherapi.com
    # 准备请求头，包含认证信息和接受Gzip压缩
    headers = {
            'X-QW-Api-Key': api_key,  # 核心修改：将Key放入请求头[citation:2]
            'Accept-Encoding': 'gzip'  # 接受压缩数据以节省流量
    }
    # 注意：host部分替换为您的专属域名，路径部分保持不变
    geo_url = f"https://{your_api_host}/geo/v2/city/lookup?location={'重庆'}"
    # 发送请求时传入 headers
    geo_resp = requests.get(geo_url, headers=headers).json()
    location_id = geo_resp['location'][0]['id']
    city_name = geo_resp['location'][0]['name']  # 获取标准名称，如“北京市”
    print(f"{location_id} {city_name}")
    print(geo_resp)
    # 获取实时天气
    days = 3
    weather_url = f"https://{your_api_host}/v7/weather/{days}d?location={location_id}"
    weather_key = 'daily'
    #weather_key = 'now'
    weather_resp = requests.get(weather_url, headers=headers).json()
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
    print(f"{city_name}未来{days}天预报：\n" + "\n".join(summary))
    print(f"{city_name}的经纬度为：{geo_resp['location'][0]['lat']},{geo_resp['location'][0]['lon']}")
    print(get_air_quality(geo_resp['location'][0]['lat'],geo_resp['location'][0]['lon'],1))






