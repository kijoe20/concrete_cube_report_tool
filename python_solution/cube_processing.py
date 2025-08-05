# cube_processing.py
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

RAW_SHEET = "Raw"
TARGET_SHEETS = ["45D", "60D", "45DWP", "60DWP"]

def get_strict_type(mark: str) -> str:
    """複製 VBA GetStrictConcreteType 的邏輯"""
    mark = mark.upper()
    is45 = "45D" in mark
    is60 = "60D" in mark
    is_wp = "WP"  in mark
    if is45 and is_wp:
        return "45DWP"
    if is60 and is_wp:
        return "60DWP"
    if is45:
        return "45D"
    if is60:
        return "60D"
    return "Unknown"

def create_or_clear(ws_name: str, wb) -> Worksheet:
    """若工作表不存在就建立，若存在就清空"""
    if ws_name in wb.sheetnames:
        ws = wb[ws_name]
        ws.delete_rows(1, ws.max_row)        # 清空(保留表)
    else:
        ws = wb.create_sheet(title=ws_name)
    return ws

def split_by_type(wb):
    src = wb[RAW_SHEET]
    # 建四個目標工作表並複製表頭
    targets = {t: create_or_clear(t, wb) for t in TARGET_SHEETS}
    for t_ws in targets.values():
        for row in src.iter_rows(min_row=1, max_row=1, values_only=False):
            t_ws.append([cell.value for cell in row])
    # 逐列判斷並複製
    for r in src.iter_rows(min_row=2, values_only=False):
        mark = r[0].value                       # A 欄
        t_type = get_strict_type(mark)
        if t_type in targets:
            targets[t_type].append([cell.value for cell in r])

def merge_pour_locations(ws: Worksheet, col_letter: str = "G"):
    """把澆築位置欄(G) 連續相同值的儲格垂直合併"""
    col = ws[col_letter]
    i, last = 2, ws.max_row
    while i <= last:
        start = i
        curr = ws[f"{col_letter}{i}"].value
        # 找同值區段
        while i <= last and ws[f"{col_letter}{i}"].value == curr:
            i += 1
        if i - start > 1:
            ws.merge_cells(start_row=start, start_column=col[0].column,
                           end_row=i-1,  end_column=col[0].column)
            cell = ws[f"{col_letter}{start}"]
            cell.alignment = cell.alignment.copy(vertical="center")

def merge_every_two(ws: Worksheet, col_letter: str):
    """指定欄位每兩列垂直合併 (A/B)"""
    for row in range(2, ws.max_row, 2):
        if row+1 <= ws.max_row:
            ws.merge_cells(f"{col_letter}{row}:{col_letter}{row+1}")
            cell = ws[f"{col_letter}{row}"]
            cell.alignment = cell.alignment.copy(vertical="center")

def run_all():
    wb = load_workbook("cube_data.xlsx")        # ← 你的原工作簿名
    split_by_type(wb)

    for name in TARGET_SHEETS:
        ws = wb[name]
        merge_pour_locations(ws, "G")
        merge_every_two(ws, "A")
        merge_every_two(ws, "B")

    wb.save("cube_data_processed.xlsx")         # ← 產出結果檔

if __name__ == "__main__":
    run_all()