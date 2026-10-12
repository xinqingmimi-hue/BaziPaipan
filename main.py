import flet as ft
import asyncio
import re
from datetime import datetime, timedelta
from lunar_python import Solar

# ========== 基础数据 ==========
TIANGAN = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
DIZHI   = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]

ZHI_GONG = {"子":1, "丑":8, "寅":8, "卯":3, "辰":4, "巳":4, "午":9, "未":2, "申":2, "酉":7, "戌":6, "亥":6}
GONG_NAME = {1:"坎1",2:"坤2",3:"震3",4:"巽4",5:"中5",6:"乾6",7:"兑7",8:"艮8",9:"离9"}
DUI_CHONG = {1:9,2:8,3:7,4:6,5:5,6:4,7:3,8:2,9:1}

TERM_TO_YUEJIANG = {"大雪": "丑", "小寒": "子", "立春": "亥", "惊蛰": "戌", "清明": "酉", "立夏": "申", "芒种": "未", "小暑": "午", "立秋": "巳", "白露": "辰", "寒露": "卯", "立冬": "寅"}

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

SHI_RANGE = {"子": (23, 1), "丑": (1, 3), "寅": (3, 5), "卯": (5, 7), "辰": (7, 9), "巳": (9, 11), "午": (11, 13), "未": (13, 15), "申": (15, 17), "酉": (17, 19), "戌": (19, 21), "亥": (21, 23)}
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

def get_year_ganzhi_by_year(year): return TIANGAN[(year - 4) % 10] + DIZHI[(year - 4) % 12]

def get_bazi(dt):
    if "立春" + str(dt.year) in SOLAR_TERMS:
        if dt >= SOLAR_TERMS["立春" + str(dt.year)]: year_ganzhi = get_year_ganzhi_by_year(dt.year)
        else: year_ganzhi = get_year_ganzhi_by_year(dt.year - 1)
    else: year_ganzhi = get_year_ganzhi_by_year(dt.year) if dt >= datetime(dt.year, 2, 4) else get_year_ganzhi_by_year(dt.year - 1)

    solar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    lunar = solar.getLunar()
    eight = lunar.getEightChar()
    return {"年柱": year_ganzhi, "月柱": eight.getMonth(), "日柱": eight.getDay(), "时柱": eight.getTime(), "生肖": lunar.getYearShengXiao(), "星座": solar.getXingZuo(), "农历": lunar.toString(), "星期": solar.getWeekInChinese()}

def main(page: ft.Page):
    page.theme = ft.Theme(font_family="Microsoft YaHei")
    page.title = "万年历排盘"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 550
    page.window.height = 950
    page.padding = 15
    page.scroll = ft.ScrollMode.AUTO

    state = {"display_year": datetime.now().year, "display_month": datetime.now().month, "selected_date": datetime.now().date()}

    # --- UI组件 ---
    live_time_text = ft.Text("", size=14, color=ft.Colors.GREY_700)
    live_bazi_text = ft.Text("", size=20, weight="bold", color=ft.Colors.BLUE)
    month_title = ft.Text("", size=20, weight="bold")
    week_header = ft.Row([ft.Text(day, width=45, text_align="center", weight="bold", color=ft.Colors.GREY_600) for day in ["日","一","二","三","四","五","六"]], alignment=ft.MainAxisAlignment.CENTER, spacing=2)
    calendar_grid = ft.Column(spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    selected_date_title = ft.Text("", size=16, weight="bold", color=ft.Colors.PURPLE)
    hours_list = ft.Column(spacing=4)
    
    # 按日时反查年份
    day_hour_query_input = ft.TextField(label="日时反查 (如: 己巳 乙丑)", width=180)
    year_dropdown = ft.Dropdown(
        label="选择起始年份",
        width=150,
        options=[ft.dropdown.Option(str(y)) for y in range(2026, 2033)],
        value=str(datetime.now().year),
        text_align="center"
    )
    year_query_result = ft.Column(spacing=6)

    def update_live_info():
        now = datetime.now()
        bazi = get_bazi(now)
        live_time_text.value = f"当前：{now.strftime('%Y年%m月%d日 %H:%M:%S')} 星期{now.weekday()+1} | 农历：{bazi['农历']}"
        live_bazi_text.value = f"{bazi['年柱']} {bazi['月柱']} {bazi['日柱']} {bazi['时柱']}"
        page.update()

    async def on_timer():
        while True:
            update_live_info()
            await asyncio.sleep(1)

    def render_calendar():
        y, m = state["display_year"], state["display_month"]
        month_title.value = f"{y}年 {m}月"
        first_day = datetime(y, m, 1)
        start_weekday = (first_day.weekday() + 1) % 7
        if m == 12: next_month = datetime(y + 1, 1, 1)
        else: next_month = datetime(y, m + 1, 1)
        days_in_month = (next_month - first_day).days

        calendar_grid.controls.clear()
        row = []
        for _ in range(start_weekday): row.append(ft.Container(width=45, height=55, bgcolor=ft.Colors.TRANSPARENT))

        for day in range(1, days_in_month + 1):
            dt = datetime(y, m, day).date()
            lunar = Solar.fromYmd(y, m, day).getLunar()
            day_ganzhi = lunar.getDayInGanZhi()
            is_today = (dt == datetime.now().date())
            is_selected = (dt == state["selected_date"])
            
            if is_selected: bgcolor, text_color = ft.Colors.PURPLE_200, ft.Colors.WHITE
            elif is_today: bgcolor, text_color = ft.Colors.AMBER_100, ft.Colors.BLACK
            else: bgcolor, text_color = ft.Colors.WHITE, ft.Colors.BLACK

            cell = ft.Container(width=45, height=55, bgcolor=bgcolor, border_radius=5,
                on_click=lambda e, d=dt: on_date_click(d),
                content=ft.Column([ft.Text(str(day), size=14, weight="bold", color=text_color),
                                   ft.Text(day_ganzhi, size=10, color=ft.Colors.GREY_700 if not is_selected else ft.Colors.WHITE)],
                                  spacing=0, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER))
            row.append(cell)
            if len(row) == 7:
                calendar_grid.controls.append(ft.Row(row, alignment=ft.MainAxisAlignment.CENTER, spacing=2))
                row = []
        if row:
            while len(row) < 7: row.append(ft.Container(width=45, height=55, bgcolor=ft.Colors.TRANSPARENT))
            calendar_grid.controls.append(ft.Row(row, alignment=ft.MainAxisAlignment.CENTER, spacing=2))
        page.update()

    def on_date_click(dt):
        state["selected_date"] = dt
        render_calendar()
        render_hours(dt)

    def render_hours(dt):
        selected_date_title.value = f"选中日期：{dt.strftime('%Y年%m月%d日')} 的十二时辰"
        hours_list.controls.clear()
        for hour in [23, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21]:
            base_dt = datetime(dt.year, dt.month, dt.day, 23 if hour == 23 else hour, 0)
            bazi = get_bazi(base_dt)
            shi_zhi = get_shi_zhi(base_dt)
            start_str, end_str = get_shi_span(base_dt)
            hours_list.controls.append(ft.Row([ft.Text(f"{shi_zhi}时", width=40, weight="bold", color=ft.Colors.PURPLE),
                                               ft.Text(f"{start_str}-{end_str}", width=90, size=12),
                                               ft.Text(f"{bazi['年柱']} {bazi['月柱']} {bazi['日柱']} {bazi['时柱']}", size=14, weight="bold")],
                                              alignment=ft.MainAxisAlignment.CENTER, spacing=10))
        page.update()

    def prev_month(e):
        if state["display_month"] == 1: state["display_month"], state["display_year"] = 12, state["display_year"] - 1
        else: state["display_month"] -= 1
        render_calendar()
    def next_month(e):
        if state["display_month"] == 12: state["display_month"], state["display_year"] = 1, state["display_year"] + 1
        else: state["display_month"] += 1
        render_calendar()
    def go_today(e):
        today = datetime.now()
        state["display_year"], state["display_month"], state["selected_date"] = today.year, today.month, today.date()
        render_calendar(); render_hours(state["selected_date"])

    def clean_input(text):
        """去除空格及各种标点符号，返回按2个字一组的列表"""
        text = re.sub(r'\s+', '', text) # 去除所有空白字符
        text = re.sub(r'[、，,\.。]', '', text) # 去除标点
        if len(text) == 8: return [text[i:i+2] for i in range(0, 8, 2)]
        return [text[i:i+2] for i in range(0, len(text), 2)]

    def do_year_query(e):
        """按日时反查指定年份区间"""
        year_query_result.controls.clear()
        input_str = day_hour_query_input.value
        if not input_str:
            year_query_result.controls.append(ft.Text("请输入日时（如：己巳 乙丑）", color=ft.Colors.RED))
            page.update(); return
            
        parts = clean_input(input_str)
        if len(parts) != 2:
            year_query_result.controls.append(ft.Text("格式错误，请输入两个柱（如：己巳乙丑 或 己巳 乙丑）", color=ft.Colors.RED))
            page.update(); return

        selected_year = int(year_dropdown.value)
        current_year = datetime.now().year
        
        # 默认逻辑：如果选的是今年，查“今天起往后365天”；如果是其他年份，查“那一年全年”
        if selected_year == current_year:
            start_date = datetime.now()
            end_date = start_date + timedelta(days=365)
            hint_text = f"正在检索 {selected_year} 年（从今天起算一年内），符合 {parts[0]}日 {parts[1]}时 的所有日期..."
        else:
            start_date = datetime(selected_year, 1, 1)
            end_date = datetime(selected_year, 12, 31)
            hint_text = f"正在检索 {selected_year} 年，符合 {parts[0]}日 {parts[1]}时 的所有日期..."
        
        # 添加临时的“正在检索”提示
        year_query_result.controls.append(ft.Text(hint_text, color=ft.Colors.BLUE))
        page.update()
        
        found = False
        current_date = start_date
        
        while current_date <= end_date:
            # 由于 start_date 可能跨年，构建 dt 时必须使用 current_date 的年月日
            y, m, d = current_date.year, current_date.month, current_date.day
            try:
                dt = datetime(y, m, d, 0, 0)
                bazi = get_bazi(dt)
                if bazi["日柱"] == parts[0]:
                    for hour in [23, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21]:
                        h_dt = datetime(y, m, d, hour, 0)
                        h_bazi = get_bazi(h_dt)
                        if h_bazi["时柱"] == parts[1]:
                            start_str, end_str = get_shi_span(h_dt)
                            # 添加结果行
                            year_query_result.controls.append(
                                ft.Text(f"公历：{h_dt.strftime('%Y-%m-%d')} {start_str}-{end_str} | 农历：{h_bazi['农历']}", color=ft.Colors.GREEN)
                            )
                            year_query_result.controls.append(
                                ft.Text(f"八字：{h_bazi['年柱']} {h_bazi['月柱']} {h_bazi['日柱']} {h_bazi['时柱']}", size=12, color=ft.Colors.GREY_700)
                            )
                            found = True
            except: pass
            current_date += timedelta(days=1)
        
        # 清除“正在检索”的临时提示（如果存在且是第一个元素）
        if len(year_query_result.controls) > 0 and isinstance(year_query_result.controls[0], ft.Text) and "正在检索" in year_query_result.controls[0].value:
            year_query_result.controls.pop(0)
            
        if not found:
            year_query_result.controls.append(ft.Text(f"{selected_year} 年内未找到符合 {parts[0]}日 {parts[1]}时 的日期", color=ft.Colors.RED))
        page.update()

    # ---------- 布局 ----------
    page.add(
        ft.Column([
            ft.Container(content=ft.Column([live_time_text, live_bazi_text], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=10, bgcolor=ft.Colors.BLUE_50, border_radius=10),
            ft.Divider(height=5),
            ft.Row([ft.IconButton(icon=ft.Icons.ARROW_LEFT, on_click=prev_month), month_title, ft.IconButton(icon=ft.Icons.ARROW_RIGHT, on_click=next_month), ft.Button("回今天", on_click=go_today)], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            week_header, calendar_grid, ft.Divider(height=10),
            selected_date_title, hours_list, ft.Divider(height=10),
            
            ft.Text("📅 日时反查（查某一年内符合此日时的所有日期）", size=14, weight="bold", color=ft.Colors.BLUE),
            ft.Row([day_hour_query_input, year_dropdown], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ft.Row([ft.Button("开始反查", on_click=do_year_query)], alignment=ft.MainAxisAlignment.CENTER),
            year_query_result,
            ft.Divider(height=20)
        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    render_calendar(); render_hours(state["selected_date"]); update_live_info()
    page.run_task(on_timer)

if __name__ == "__main__":
    ft.run(main)
