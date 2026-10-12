import flet as ft
from datetime import datetime, timedelta
from lunar_python import Solar

# ========== 基础数据 ==========
TIANGAN = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
DIZHI   = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]

# 九宫映射
ZHI_GONG = {
    "子":1, "丑":8, "寅":8, "卯":3, "辰":4, "巳":4,
    "午":9, "未":2, "申":2, "酉":7, "戌":6, "亥":6
}
GONG_NAME = {1:"坎1",2:"坤2",3:"震3",4:"巽4",5:"中5",6:"乾6",7:"兑7",8:"艮8",9:"离9"}
DUI_CHONG = {1:9,2:8,3:7,4:6,5:5,6:4,7:3,8:2,9:1}

# ========== 节气与月将映射 ==========
TERM_TO_YUEJIANG = {
    "大雪": "丑", "小寒": "子", "立春": "亥", "惊蛰": "戌", "清明": "酉",
    "立夏": "申", "芒种": "未", "小暑": "午", "立秋": "巳", "白露": "辰",
    "寒露": "卯", "立冬": "寅",
}

# ========== 2026-2032年节气数据 ==========
SOLAR_TERMS = {
    "大雪2025": datetime(2025, 12, 7, 6, 33),
    "小寒2026": datetime(2026, 1, 5, 16, 23), "立春2026": datetime(2026, 2, 4, 4, 2),
    "惊蛰2026": datetime(2026, 3, 5, 21, 59), "清明2026": datetime(2026, 4, 5, 2, 40),
    "立夏2026": datetime(2026, 5, 5, 19, 49), "芒种2026": datetime(2026, 6, 5, 23, 48),
    "小暑2026": datetime(2026, 7, 7, 9, 57), "立秋2026": datetime(2026, 8, 7, 19, 43),
    "白露2026": datetime(2026, 9, 7, 22, 41), "寒露2026": datetime(2026, 10, 8, 14, 29),
    "立冬2026": datetime(2026, 11, 7, 17, 52), "大雪2026": datetime(2026, 12, 7, 10, 53),
    "小寒2027": datetime(2027, 1, 5, 22, 9), "立春2027": datetime(2027, 2, 4, 9, 46),
    "惊蛰2027": datetime(2027, 3, 6, 3, 39), "清明2027": datetime(2027, 4, 5, 8, 17),
    "立夏2027": datetime(2027, 5, 6, 1, 24), "芒种2027": datetime(2027, 6, 6, 5, 25),
    "小暑2027": datetime(2027, 7, 7, 15, 36), "立秋2027": datetime(2027, 8, 8, 1, 26),
    "白露2027": datetime(2027, 9, 8, 4, 28), "寒露2027": datetime(2027, 10, 8, 20, 16),
    "立冬2027": datetime(2027, 11, 7, 23, 38), "大雪2027": datetime(2027, 12, 7, 16, 37),
    "小寒2028": datetime(2028, 1, 6, 3, 52), "立春2028": datetime(2028, 2, 4, 15, 30),
    "惊蛰2028": datetime(2028, 3, 5, 9, 24), "清明2028": datetime(2028, 4, 4, 14, 2),
    "立夏2028": datetime(2028, 5, 5, 7, 11), "芒种2028": datetime(2028, 6, 5, 11, 15),
    "小暑2028": datetime(2028, 7, 6, 21, 29), "立秋2028": datetime(2028, 8, 7, 7, 20),
    "白露2028": datetime(2028, 9, 7, 10, 21), "寒露2028": datetime(2028, 10, 8, 2, 8),
    "立冬2028": datetime(2028, 11, 7, 5, 26), "大雪2028": datetime(2028, 12, 6, 22, 24),
    "小寒2029": datetime(2029, 1, 5, 9, 41), "立春2029": datetime(2029, 2, 3, 21, 20),
    "惊蛰2029": datetime(2029, 3, 5, 15, 17), "清明2029": datetime(2029, 4, 4, 19, 58),
    "立夏2029": datetime(2029, 5, 5, 13, 7), "芒种2029": datetime(2029, 6, 5, 17, 9),
    "小暑2029": datetime(2029, 7, 7, 3, 22), "立秋2029": datetime(2029, 8, 7, 13, 11),
    "白露2029": datetime(2029, 9, 7, 16, 11), "寒露2029": datetime(2029, 10, 8, 7, 57),
    "立冬2029": datetime(2029, 11, 7, 11, 16), "大雪2029": datetime(2029, 12, 7, 4, 13),
    "小寒2030": datetime(2030, 1, 5, 15, 30), "立春2030": datetime(2030, 2, 4, 3, 8),
    "惊蛰2030": datetime(2030, 3, 5, 21, 2), "清明2030": datetime(2030, 4, 5, 1, 40),
    "立夏2030": datetime(2030, 5, 5, 18, 45), "芒种2030": datetime(2030, 6, 5, 22, 44),
    "小暑2030": datetime(2030, 7, 7, 8, 55), "立秋2030": datetime(2030, 8, 7, 18, 46),
    "白露2030": datetime(2030, 9, 7, 21, 52), "寒露2030": datetime(2030, 10, 8, 13, 44),
    "立冬2030": datetime(2030, 11, 7, 17, 8), "大雪2030": datetime(2030, 12, 7, 10, 7),
    "小寒2031": datetime(2031, 1, 5, 21, 22), "立春2031": datetime(2031, 2, 4, 9, 8),
    "惊蛰2031": datetime(2031, 3, 6, 3, 2), "清明2031": datetime(2031, 4, 5, 7, 37),
    "立夏2031": datetime(2031, 5, 6, 0, 41), "芒种2031": datetime(2031, 6, 6, 4, 39),
    "小暑2031": datetime(2031, 7, 7, 14, 48), "立秋2031": datetime(2031, 8, 8, 0, 38),
    "白露2031": datetime(2031, 9, 8, 3, 42), "寒露2031": datetime(2031, 10, 8, 19, 34),
    "立冬2031": datetime(2031, 11, 7, 23, 0), "大雪2031": datetime(2031, 12, 7, 16, 3),
    "小寒2032": datetime(2032, 1, 6, 8, 59), "立春2032": datetime(2032, 2, 4, 14, 48),
    "惊蛰2032": datetime(2032, 3, 5, 8, 39), "清明2032": datetime(2032, 4, 4, 13, 17),
    "立夏2032": datetime(2032, 5, 5, 6, 25), "芒种2032": datetime(2032, 6, 5, 10, 27),
    "小暑2032": datetime(2032, 7, 6, 20, 40), "立秋2032": datetime(2032, 8, 7, 6, 32),
    "白露2032": datetime(2032, 9, 7, 9, 37), "寒露2032": datetime(2032, 10, 8, 1, 29),
    "立冬2032": datetime(2032, 11, 7, 4, 53), "大雪2032": datetime(2032, 12, 6, 21, 52),
    "小寒2033": datetime(2033, 1, 5, 8, 59),
}

sorted_terms = sorted([(name.rstrip("0123456789"), dt) for name, dt in SOLAR_TERMS.items()], key=lambda x: x[1])
YUEJIANG_INTERVALS = []
for i in range(len(sorted_terms) - 1):
    term_name, start_dt = sorted_terms[i]
    _, end_dt = sorted_terms[i + 1]
    if term_name in TERM_TO_YUEJIANG:
        YUEJIANG_INTERVALS.append((TERM_TO_YUEJIANG[term_name], start_dt, end_dt))

def get_current_yuejiang(dt):
    for yj, start, end in YUEJIANG_INTERVALS:
        if start <= dt < end: return yj, start, end
    return YUEJIANG_INTERVALS[0][0], YUEJIANG_INTERVALS[0][1], YUEJIANG_INTERVALS[0][2]

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
        if end_h < start_h: end = end.replace(day=end.day+1)
    return start.strftime("%H:%M"), end.strftime("%H:%M")

# ========== 八字计算 ==========
def get_year_ganzhi_by_year(year):
    return TIANGAN[(year - 4) % 10] + DIZHI[(year - 4) % 12]

def get_bazi(dt):
    if "立春" + str(dt.year) in SOLAR_TERMS:
        if dt >= SOLAR_TERMS["立春" + str(dt.year)]: year_ganzhi = get_year_ganzhi_by_year(dt.year)
        else: year_ganzhi = get_year_ganzhi_by_year(dt.year - 1)
    else: year_ganzhi = get_year_ganzhi_by_year(dt.year) if dt >= datetime(dt.year, 2, 4) else get_year_ganzhi_by_year(dt.year - 1)

    solar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    lunar = solar.getLunar()
    eight = lunar.getEightChar()
    return {
        "年柱": year_ganzhi, "月柱": eight.getMonth(), "日柱": eight.getDay(), "时柱": eight.getTime(),
        "生肖": lunar.getYearShengXiao(), "星座": solar.getXingZuo(),
        "农历": lunar.toString(), "星期": solar.getWeekInChinese(),
    }

# ========== 神煞与月将算法 ==========
def yuejiang_jia_shi(yuejiang, shi, target_zhi):
    zhi_list = DIZHI
    target_idx_in_jialin = (zhi_list.index(target_zhi) - zhi_list.index(yuejiang)) % 12
    shi_idx = zhi_list.index(shi)
    luo_zhi_idx = (shi_idx + target_idx_in_jialin) % 12
    return ZHI_GONG[zhi_list[luo_zhi_idx]]

def get_tingting(yj, shi): return ("子", yuejiang_jia_shi(yj, shi, "子"))
def get_tiangang(yj, shi): return ("辰", yuejiang_jia_shi(yj, shi, "辰"))
def get_tianmen(yj, shi): return {"卯": yuejiang_jia_shi(yj, shi, "卯"), "未": yuejiang_jia_shi(yj, shi, "未"), "酉": yuejiang_jia_shi(yj, shi, "酉")}
def get_baihan(tt_gong): return DUI_CHONG.get(tt_gong, tt_gong)

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
        start_bj = day_start.replace(hour=hour) if hour != 23 else day_start.replace(hour=23)
        bazi = get_bazi(start_bj)
        if bazi["时柱"] in TIANXIAN_MAP.get(ri_gan, []):
            start_str, end_str = get_shi_span(start_bj)
            result.append({"shizhu": bazi["时柱"], "start": start_str, "end": end_str, "bazi": f"{bazi['年柱']} {bazi['月柱']} {bazi['日柱']} {bazi['时柱']}"})
    result.sort(key=lambda x: x["start"])
    return result

# ========== Flet界面 ==========
def main(page: ft.Page):
    page.theme = ft.Theme(font_family="Microsoft YaHei")
    page.title = "八字排盘（2026-2032年，北京时间）"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 550
    page.window.height = 850
    page.window.resizable = True
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    now = datetime.now()
    if now.year < 2026 or now.year > 2032:
        now = now.replace(year=2026)
    
    # 这里就是修复出屏的地方，将 width 改小到 50，间距改小
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
        if n.year < 2026 or n.year > 2032: n = n.replace(year=2026)
        year_in.value = str(n.year); month_in.value = str(n.month); day_in.value = str(n.day)
        hour_in.value = str(n.hour); minute_in.value = str(n.minute)
        current_dt = n
        page.update()
        calculate(None)

    def calculate(e=None):
        nonlocal current_dt
        try:
            y = int(year_in.value); m = int(month_in.value); d = int(day_in.value)
            h = int(hour_in.value); minute = int(minute_in.value)
            if y < 2026 or y > 2032: raise ValueError("年份仅支持2026-2032")
            dt = datetime(y, m, d, h, minute)
        except Exception as ex:
            msg_text.value = f"输入错误：{ex}"
            page.update(); return

        current_dt = dt
        bazi = get_bazi(dt)
        bazi_text.value = f"{bazi['年柱']} {bazi['月柱']} {bazi['日柱']} {bazi['时柱']}"
        lunar_info.value = f"{bazi['农历']} 生肖:{bazi['生肖']} 星座:{bazi['星座']} 星期:{bazi['星期']}"

        yj, yj_start, yj_end = get_current_yuejiang(dt)
        yuejiang_info.value = f"月将：{yj}将（{yj_start.strftime('%m月%d日 %H:%M')} - {yj_end.strftime('%m月%d日 %H:%M')}）"

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
                tianxian_column.controls.append(ft.Text(f"{item['shizhu']} ({item['start']} - {item['end']})", size=14, color=ft.Colors.GREEN))
                tianxian_column.controls.append(ft.Text(f"八字：{item['bazi']}", size=12, color=ft.Colors.GREY_700))
        else:
            tianxian_column.controls.append(ft.Text("今日无天显时格", size=14, color=ft.Colors.GREY))

        msg_text.value = ""
        page.update()

    def prev_day(e):
        nonlocal current_dt
        new_dt = current_dt - timedelta(days=1)
        if new_dt.year < 2026 or new_dt.year > 2032: new_dt = current_dt
        else: update_inputs(new_dt); calculate()

    def next_day(e):
        nonlocal current_dt
        new_dt = current_dt + timedelta(days=1)
        if new_dt.year < 2026 or new_dt.year > 2032: new_dt = current_dt
        else: update_inputs(new_dt); calculate()

    def prev_shi(e):
        nonlocal current_dt
        new_dt = current_dt - timedelta(hours=2)
        if new_dt.year < 2026 or new_dt.year > 2032: new_dt = current_dt
        else: update_inputs(new_dt); calculate()

    def next_shi(e):
        nonlocal current_dt
        new_dt = current_dt + timedelta(hours=2)
        if new_dt.year < 2026 or new_dt.year > 2032: new_dt = current_dt
        else: update_inputs(new_dt); calculate()

    def update_inputs(dt):
        year_in.value = str(dt.year); month_in.value = str(dt.month); day_in.value = str(dt.day)
        hour_in.value = str(dt.hour); minute_in.value = str(dt.minute)
        nonlocal current_dt
        current_dt = dt

    # 这里就是修复出屏的地方，间距改小到 5
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
            ft.Text("八字排盘 (2026-2032)", size=24, weight="bold", text_align=ft.TextAlign.CENTER),
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
