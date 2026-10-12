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

# ========== 时辰辅助函数 ==========
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

# ========== 八字计算（动态计算节气，支持1900-2100） ==========
def get_bazi(dt):
    solar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    lunar = solar.getLunar()
    eight = lunar.getEightChar()
    return {
        "年柱": eight.getYear(), "月柱": eight.getMonth(), "日柱": eight.getDay(), "时柱": eight.getTime(),
        "生肖": lunar.getYearShengXiao(), "星座": solar.getXingZuo(),
        "农历": lunar.toString(), "星期": solar.getWeekInChinese(),
    }

def get_current_yuejiang(dt):
    solar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, 0)
    lunar = solar.getLunar()
    prev_jieqi = lunar.getPrevJieQi(True)
    if prev_jieqi:
        term_name = prev_jieqi.getName()
        yj = TERM_TO_YUEJIANG.get(term_name, "子")
        s = prev_jieqi.getSolar()
        start_dt = datetime(s.getYear(), s.getMonth(), s.getDay(), s.getHour(), s.getMinute(), s.getSecond())
        return yj, start_dt, term_name
    return "子", None, None

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
    page.title = "万年历排盘（1900-2100年）"
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
        options=[ft.dropdown.Option(str(y)) for y in range(1900, 2101)], # 扩大到1900-2100
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
        text = re.sub(r'\s+', '', text)
        text = re.sub(r'[、，,\.。]', '', text)
        if len(text) == 8: return [text[i:i+2] for i in range(0, 8, 2)]
        return [text[i:i+2] for i in range(0, len(text), 2)]

    def do_year_query(e):
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
        
        if selected_year == current_year:
            start_date = datetime.now()
            end_date = start_date + timedelta(days=365)
            hint_text = f"正在检索 {selected_year} 年（从今天起算一年内），符合 {parts[0]}日 {parts[1]}时 的所有日期..."
        else:
            start_date = datetime(selected_year, 1, 1)
            end_date = datetime(selected_year, 12, 31)
            hint_text = f"正在检索 {selected_year} 年，符合 {parts[0]}日 {parts[1]}时 的所有日期..."
        
        year_query_result.controls.append(ft.Text(hint_text, color=ft.Colors.BLUE))
        page.update()
        
        found = False
        current_date = start_date
        
        while current_date <= end_date:
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
                            year_query_result.controls.append(
                                ft.Text(f"公历：{h_dt.strftime('%Y-%m-%d')} {start_str}-{end_str} | 农历：{h_bazi['农历']}", color=ft.Colors.GREEN)
                            )
                            year_query_result.controls.append(
                                ft.Text(f"八字：{h_bazi['年柱']} {h_bazi['月柱']} {h_bazi['日柱']} {h_bazi['时柱']}", size=12, color=ft.Colors.GREY_700)
                            )
                            found = True
            except: pass
            current_date += timedelta(days=1)
        
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
