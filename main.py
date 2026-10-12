import flet as ft
from datetime import datetime, timedelta
from lunar_python import Solar
import asyncio
import re

# ========== 基础数据 ==========
TIANGAN = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
DIZHI   = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]

ZHI_GONG = {"子":1, "丑":8, "寅":8, "卯":3, "辰":4, "巳":4, "午":9, "未":2, "申":2, "酉":7, "戌":6, "亥":6}
GONG_NAME = {1:"坎1",2:"坤2",3:"震3",4:"巽4",5:"中5",6:"乾6",7:"兑7",8:"艮8",9:"离9"}
DUI_CHONG = {1:9,2:8,3:7,4:6,5:5,6:4,7:3,8:2,9:1}

TERM_TO_YUEJIANG = {
    "大雪": "丑", "小寒": "子", "立春": "亥", "惊蛰": "戌", "清明": "酉",
    "立夏": "申", "芒种": "未", "小暑": "午", "立秋": "巳", "白露": "辰",
    "寒露": "卯", "立冬": "寅",
}

# ========== 时辰辅助函数 ==========
SHI_RANGE = {
    "子": (23, 1), "丑": (1, 3), "寅": (3, 5), "卯": (5, 7),
    "辰": (7, 9), "巳": (9, 11), "午": (11, 13), "未": (13, 15),
    "申": (15, 17), "酉": (17, 19), "戌": (19, 21), "亥": (21, 23),
}

def get_shi_zhi(dt):
    h = dt.hour
    if h >= 23 or h < 1: return "子"
    elif 1 <= h < 3: return "丑"
    elif 3 <= h < 5: return "寅"
    elif 5 <= h < 7: return "卯"
    elif 7 <= h < 9: return "辰"
    elif 9 <= h < 11: return "巳"
    elif 11 <= h < 13: return "午"
    elif 13 <= h < 15: return "未"
    elif 15 <= h < 17: return "申"
    elif 17 <= h < 19: return "酉"
    elif 19 <= h < 21: return "戌"
    else: return "亥"

def get_shi_span(dt):
    zhi = get_shi_zhi(dt)
    start_h, end_h = SHI_RANGE[zhi]
    if start_h == 23:
        start = dt.replace(hour=23, minute=0)
        end = (dt + timedelta(days=1)).replace(hour=end_h, minute=0)
    else:
        start = dt.replace(hour=start_h, minute=0)
        end = dt.replace(hour=end_h, minute=0)
        if end_h < start_h:
            end = end.replace(day=end.day+1)
    return start.strftime("%H:%M"), end.strftime("%H:%M")

# ========== 八字计算（动态计算节气）==========
def get_year_ganzhi_by_year(year):
    gan = (year - 4) % 10
    zhi = (year - 4) % 12
    return TIANGAN[gan] + DIZHI[zhi]

def get_bazi(dt):
    solar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    lunar = solar.getLunar()
    eight = lunar.getEightChar()
    
    year_ganzhi = eight.getYear()
    
    return {
        "年柱": year_ganzhi,
        "月柱": eight.getMonth(),
        "日柱": eight.getDay(),
        "时柱": eight.getTime(),
        "生肖": lunar.getYearShengXiao(),
        "星座": solar.getXingZuo(),
        "农历": lunar.toString(),
        "星期": solar.getWeekInChinese(),
    }

def get_current_yuejiang(dt):
    """动态获取当前月将"""
    solar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, 0)
    lunar = solar.getLunar()
    prev_jieqi = lunar.getPrevJieQi(True)
    if prev_jieqi:
        term_name = prev_jieqi.getName()
        yj = TERM_TO_YUEJIANG.get(term_name, "子")
        s = prev_jieqi.getSolar()
        # 关键修复：把 Solar 对象转成 Python 的 datetime
        start_dt = datetime(s.getYear(), s.getMonth(), s.getDay(), s.getHour(), s.getMinute(), s.getSecond())
        return yj, start_dt, term_name
    return "子", None, None

# ========== 神煞函数 ==========
def yuejiang_jia_shi(yuejiang, shi, target_zhi):
    zhi_list = DIZHI
    jialin = []
    for i in range(12):
        jialin.append(zhi_list[(zhi_list.index(yuejiang) + i) % 12])
    target_idx_in_jialin = (zhi_list.index(target_zhi) - zhi_list.index(yuejiang)) % 12
    shi_idx = zhi_list.index(shi)
    luo_zhi_idx = (shi_idx + target_idx_in_jialin) % 12
    luo_zhi = zhi_list[luo_zhi_idx]
    return ZHI_GONG[luo_zhi]

def get_tingting(yj, shi):
    gong = yuejiang_jia_shi(yj, shi, "子")
    return ("子", gong)

def get_tiangang(yj, shi):
    gong = yuejiang_jia_shi(yj, shi, "辰")
    return ("辰", gong)

def get_tianmen(yj, shi):
    return {
        "卯": yuejiang_jia_shi(yj, shi, "卯"),
        "未": yuejiang_jia_shi(yj, shi, "未"),
        "酉": yuejiang_jia_shi(yj, shi, "酉"),
    }

def get_baihan(tt_gong):
    return DUI_CHONG.get(tt_gong, tt_gong)

TIANXIAN_MAP = {
    "甲": ["甲子", "甲戌"], "己": ["甲子", "甲戌"], "乙": ["甲申"], "庚": ["甲申"],
    "丙": ["甲午"], "辛": ["甲午"], "丁": ["甲辰"], "壬": ["甲辰"], "戊": ["甲寅"], "癸": ["甲寅"],
}

def get_tianxian_list(dt):
    day_start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    bazi_day = get_bazi(day_start)
    ri_gan = bazi_day["日柱"][0]
    result = []
    for hour in [23, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21]:
        if hour == 23:
            start_bj = day_start.replace(hour=23)
        else:
            start_bj = day_start.replace(hour=hour)
        bazi = get_bazi(start_bj)
        shizhu = bazi["时柱"]
        if shizhu in TIANXIAN_MAP.get(ri_gan, []):
            start_str, end_str = get_shi_span(start_bj)
            result.append({
                "shizhu": shizhu,
                "start": start_str,
                "end": end_str,
                "bazi": f"{bazi['年柱']} {bazi['月柱']} {bazi['日柱']} {bazi['时柱']}",
            })
    result.sort(key=lambda x: x["start"])
    return result

# ========== Flet界面 ==========
def main(page: ft.Page):
    page.theme = ft.Theme(font_family="Microsoft YaHei")
    page.title = "八字排盘（1900-2100年）"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 550
    page.window.height = 850
    page.window.resizable = True
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    now = datetime.now()
    month_in = ft.TextField(label="月", value=str(now.month), width=50, text_align="center")
    day_in = ft.TextField(label="日", value=str(now.day), width=50, text_align="center")
    hour_in = ft.TextField(label="时", value=str(now.hour), width=50, text_align="center")
    minute_in = ft.TextField(label="分", value=str(now.minute), width=50, text_align="center")
    year_in = ft.TextField(label="年", value=str(now.year), width=50, text_align="center")

    msg_text = ft.Text("", size=14, color=ft.Colors.RED)
    bazi_text = ft.Text("", size=18, weight="bold", color=ft.Colors.BLUE)
    lunar_info = ft.Text("", size=14)
    yuejiang_info = ft.Text("", size=14, color=ft.Colors.BROWN)
    tianxian_column = ft.Column([], spacing=5)
    shensha_text = ft.Text("", size=14, selectable=True)

    current_dt = now

    def set_now(e):
        nonlocal current_dt
        n = datetime.now()
        year_in.value = str(n.year)
        month_in.value = str(n.month)
        day_in.value = str(n.day)
        hour_in.value = str(n.hour)
        minute_in.value = str(n.minute)
        current_dt = n
        page.update()
        calculate(None)

    def calculate(e=None):
        nonlocal current_dt
        try:
            y = int(year_in.value)
            m = int(month_in.value)
            d = int(day_in.value)
            h = int(hour_in.value)
            minute = int(minute_in.value)
            if y < 1900 or y > 2100:
                raise ValueError("年份仅支持1900-2100")
            dt = datetime(y, m, d, h, minute)
        except Exception as ex:
            msg_text.value = f"输入错误：{ex}"
            page.update()
            return

        current_dt = dt
        bazi = get_bazi(dt)
        bazi_text.value = f"{bazi['年柱']} {bazi['月柱']} {bazi['日柱']} {bazi['时柱']}"
        lunar_info.value = f"{bazi['农历']} 生肖:{bazi['生肖']} 星座:{bazi['星座']} 星期:{bazi['星期']}"

        yj, yj_start, _ = get_current_yuejiang(dt)
        if yj_start:
            yuejiang_info.value = f"月将：{yj}将（{yj_start.strftime('%m月%d日 %H:%M')} 起）"
        else:
            yuejiang_info.value = f"月将：{yj}将"

        shi_zhi = get_shi_zhi(dt)
        tt_zhi, tt_gong = get_tingting(yj, shi_zhi)
        tg_zhi, tg_gong = get_tiangang(yj, shi_zhi)
        bh_gong = get_baihan(tt_gong)
        tianmen = get_tianmen(yj, shi_zhi)
        bh_zhi = next((z for z, g in ZHI_GONG.items() if g == bh_gong), "子")

        shensha_text.value = (
            f"月将:{yj} 亭亭:{tt_zhi}({GONG_NAME[tt_gong]}) 白奸:{bh_zhi}({GONG_NAME[bh_gong]}) | "
            f"天罡:{tg_zhi}({GONG_NAME[tg_gong]}) | "
            f"天三门:卯({GONG_NAME[tianmen['卯']]},天马) 未({GONG_NAME[tianmen['未']]}) 酉({GONG_NAME[tianmen['酉']]})"
        )

        tianxian_list = get_tianxian_list(dt)
        tianxian_column.controls.clear()
        if tianxian_list:
            for item in tianxian_list:
                tianxian_column.controls.append(
                    ft.Text(f"{item['shizhu']} ({item['start']} - {item['end']})", size=14, color=ft.Colors.GREEN)
                )
                tianxian_column.controls.append(
                    ft.Text(f"八字：{item['bazi']}", size=12, color=ft.Colors.GREY_700)
                )
        else:
            tianxian_column.controls.append(ft.Text("今日无天显时格", size=14, color=ft.Colors.GREY))

        msg_text.value = ""
        page.update()

    def prev_day(e):
        nonlocal current_dt
        new_dt = current_dt - timedelta(days=1)
        if new_dt.year < 1900 or new_dt.year > 2100:
            new_dt = current_dt
        else:
            update_inputs(new_dt)
            calculate()

    def next_day(e):
        nonlocal current_dt
        new_dt = current_dt + timedelta(days=1)
        if new_dt.year < 1900 or new_dt.year > 2100:
            new_dt = current_dt
        else:
            update_inputs(new_dt)
            calculate()

    def prev_shi(e):
        nonlocal current_dt
        new_dt = current_dt - timedelta(hours=2)
        if new_dt.year < 1900 or new_dt.year > 2100:
            new_dt = current_dt
        else:
            update_inputs(new_dt)
            calculate()

    def next_shi(e):
        nonlocal current_dt
        new_dt = current_dt + timedelta(hours=2)
        if new_dt.year < 1900 or new_dt.year > 2100:
            new_dt = current_dt
        else:
            update_inputs(new_dt)
            calculate()

    def update_inputs(dt):
        year_in.value = str(dt.year)
        month_in.value = str(dt.month)
        day_in.value = str(dt.day)
        hour_in.value = str(dt.hour)
        minute_in.value = str(dt.minute)
        nonlocal current_dt
        current_dt = dt

    input_row = ft.Row(
        [year_in, month_in, day_in, hour_in, minute_in],
        alignment=ft.MainAxisAlignment.CENTER, spacing=5
    )

    nav_row = ft.Row([
        ft.IconButton(icon=ft.Icons.ARROW_LEFT, tooltip="上一日", on_click=prev_day),
        ft.IconButton(icon=ft.Icons.ARROW_RIGHT, tooltip="下一日", on_click=next_day),
        ft.IconButton(icon=ft.Icons.ARROW_BACK, tooltip="上一个时辰", on_click=prev_shi),
        ft.IconButton(icon=ft.Icons.ARROW_FORWARD, tooltip="下一个时辰", on_click=next_shi),
        ft.Button("当前时间", on_click=set_now, icon=ft.Icons.UPDATE),
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)

    calc_btn = ft.Button(
        "排盘", on_click=calculate, icon=ft.Icons.CHECK,
        style=ft.ButtonStyle(bgcolor=ft.Colors.PURPLE, color=ft.Colors.WHITE)
    )

    info_column = ft.Column([
        ft.Text("八字：", size=16),
        bazi_text,
        lunar_info,
        ft.Divider(height=10),
        yuejiang_info,
        ft.Divider(height=10),
        ft.Text("今日天显时格（北京时间）：", size=16, weight="bold"),
        tianxian_column,
        ft.Divider(height=10),
        ft.Text("神煞方位：", size=16, weight="bold"),
        shensha_text,
    ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    page.add(
        ft.Column([
            ft.Text("八字排盘 (1900-2100)", size=24, weight="bold", text_align=ft.TextAlign.CENTER),
            input_row,
            nav_row,
            calc_btn,
            msg_text,
            info_column,
        ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)
    )

    calculate()

if __name__ == "__main__":
    ft.run(main)
