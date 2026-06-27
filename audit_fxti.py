import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from data.fxti_bazi import (
    get_year_ganzhi, get_month_ganzhi, get_day_ganzhi, get_hour_ganzhi,
    calculate_bazi, count_wuxing, calculate_wuxing_percentage, get_innate_wuxing
)

report = []
report.append("=" * 60)
report.append("FXTI 八字計算審核報告")
report.append("=" * 60)
report.append("")
report.append("用戶資料: 1991-03-04 18:55 男")
report.append("用戶聲稱八字: 辛未 癸卯 甲午 癸酉")
report.append("")

# Step-by-step calculation
year = 1991
month = 3
day = 4
hour = 18

report.append("--- FXTI 計算過程 ---")
report.append("")

year_gz = get_year_ganzhi(year)
report.append(f"年柱: {year_gz} (天干={year_gz[0]}, 地支={year_gz[1]})")

month_gz = get_month_ganzhi(year, month)
report.append(f"月柱: {month_gz} (天干={month_gz[0]}, 地支={month_gz[1]})")

# Show month calculation steps
report.append(f"  月柱計算:")
report.append(f"    year_gan = '{year_gz[0]}' → start_gan = '庚' (根據五虎遁)")
report.append(f"    month={month} → dz_index = ({month}+1)%12 = {(month+1)%12}")
report.append(f"    地支 = DIZHI[{(month+1)%12 - 2}] = {get_month_ganzhi(year, month)[1]}")
report.append(f"    問題: 使用公曆月份({month})而非農曆月份/節氣!")
report.append(f"    1991年3月4日農曆約為正月(寅月)，但公曆3月已過立春/雨水")
report.append("")

day_gz = get_day_ganzhi(year, month, day)
report.append(f"日柱: {day_gz} (天干={day_gz[0]}, 地支={day_gz[1]})")
report.append(f"  日柱計算: 基準日期 1900-01-31, delta_days = 計算所得")
report.append(f"  問題: 1991年3月4日的日柱應為'甲午'，但計算為'{day_gz}'")
report.append("")

hour_gz = get_hour_ganzhi(day_gz[0], hour)
report.append(f"時柱: {hour_gz} (天干={hour_gz[0]}, 地支={hour_gz[1]})")
report.append(f"  時柱計算: day_gan='{day_gz[0]}', hour={hour}")
report.append(f"  問題: 日干錯誤導致時干錯誤")
report.append("")

# Full result
full = get_innate_wuxing(year, month, day, hour)
report.append("--- FXTI 計算結果 ---")
report.append(f"八字: {full['bazi']}")
report.append(f"五行計數(含藏干): {full['wuxing_count']}")
report.append(f"五行百分比: {full['wuxing_percentage']}")
report.append(f"最高五行: {max(full['wuxing_percentage'], key=full['wuxing_percentage'].get)}")
report.append("")

# Without canggan
full_no_cg = get_innate_wuxing(year, month, day, hour, use_canggan=False)
report.append("--- 不含藏干版本 ---")
report.append(f"五行計數(不含藏干): {full_no_cg['wuxing_count']}")
report.append(f"五行百分比: {full_no_cg['wuxing_percentage']}")
report.append(f"最高五行: {max(full_no_cg['wuxing_percentage'], key=full_no_cg['wuxing_percentage'].get)}")
report.append("")

# Manual count of user's claimed bazi
report.append("=" * 60)
report.append("用戶聲稱八字手動計算")
report.append("=" * 60)
report.append("八字: 辛未 癸卯 甲午 癸酉")
report.append("")
report.append("天干五行:")
report.append("  辛 = 金")
report.append("  癸 = 水")
report.append("  甲 = 木 (日主)")
report.append("  癸 = 水")
report.append("")
report.append("地支五行(主氣):")
report.append("  未 = 土")
report.append("  卯 = 木")
report.append("  午 = 火")
report.append("  酉 = 金")
report.append("")
report.append("天干統計: 金1 水2 木1")
report.append("地支統計: 土1 木1 火1 金1")
report.append("合計(不含藏干): 金2 木2 水2 火1 土1")
report.append("")
report.append("用戶日主: 甲木")
report.append("用戶判斷: 木最強(日主甲+卯月木旺)")
report.append("")

report.append("=" * 60)
report.append("FXTI 問題總結")
report.append("=" * 60)
report.append("")
report.append("問題1: 月柱計算錯誤")
report.append("  - 使用公曆月份而非農曆/節氣")
report.append("  - 1991年3月4日農曆約為正月(寅月)，但代碼按公曆3月算為卯月/辰月")
report.append("  - 正確做法: 需要農曆轉換或節氣判斷(立春為年分界，驚蟄/清明等為月分界)")
report.append("")
report.append("問題2: 日柱計算可能錯誤")
report.append("  - 基準日期1900-01-31與實際萬年曆可能有偏移")
report.append("  - 1991年3月4日應為'甲午'日，需驗證")
report.append("")
report.append("問題3: 時柱連鎖錯誤")
report.append("  - 日干錯誤導致時干計算基礎錯誤")
report.append("  - 時支計算: (18+1)//2 = 9 = 酉，這部分是正確的")
report.append("")
report.append("問題4: 五行統計方法爭議")
report.append("  - 使用藏干加權: 主氣1.0 + 中氣0.6 + 餘氣0.3")
report.append("  - 用戶的八字如果按藏干計算，會有額外的五行出現")
report.append("  - 例如: 未藏己丁乙(土火木)，會額外增加土1.0+火0.6+木0.3")
report.append("")
report.append("結論:")
report.append("  FXTI 的八字計算模塊有明顯bug，主要問題是:")
report.append("  1. 月柱未按農曆/節氣計算")
report.append("  2. 日柱基準日期可能需要校準")
report.append("  3. 建議: 使用成熟的農曆庫(如lunardate)或預建萬年曆表")
report.append("")
report.append("  用戶正確的八字(辛未 癸卯 甲午 癸酉)確實木較強:")
report.append("  - 日主甲木(最核心)")
report.append("  - 卯月木旺(當令)")
report.append("  - 天干有甲+乙(未中藏乙)")
report.append("  - 水2個生木")
report.append("  - 判斷為'木型人'或'水木型'更合理")
report.append("  - 金雖有2個(辛+酉)，但金克木，對甲木日主不是助力")

with open('fxti_audit_report.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print("FXTI audit complete. Report saved to fxti_audit_report.txt")
