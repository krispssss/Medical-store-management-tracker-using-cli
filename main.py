import csv
import os
from datetime import datetime


MEDICINES_FILE = 'Medicines.csv'
BATCHES_FILE = 'Batches.csv'
SALES_FILE = 'Sales.csv'

MEDICINES_HEADER = ['Medicine_Name', 'Selling_Price', 'Cost_Price', 'Stock', 'Max_Stock']
BATCHES_HEADER = ['Medicine_Name', 'Batch_No', 'Expiry_Date', 'Quantity', 'Status']
SALES_HEADER = ['Medicine_Name', 'Sale_Date', 'Qty_Sold']


MIN_COLUMNS = {MEDICINES_FILE: 5, BATCHES_FILE: 5, SALES_FILE: 3}

REORDER_PERCENT = 25
DATE_FORMAT = '%Y-%m-%d'


def setup_files():
    for filename, header in ((MEDICINES_FILE, MEDICINES_HEADER),
                             (BATCHES_FILE, BATCHES_HEADER),
                             (SALES_FILE, SALES_HEADER)):
        if not os.path.exists(filename):
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(header)


def read_csv_rows(filename):
    rows = []
    if not os.path.exists(filename):
        return rows
    need = MIN_COLUMNS.get(filename, 1)
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if not row or not any(field.strip() for field in row):
                continue
            if len(row) < need:
                continue
            rows.append([field.strip() for field in row])
    return rows


def write_csv_rows(filename, header, rows):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def get_all_medicine_names():
    return [row[0] for row in read_csv_rows(MEDICINES_FILE)]


def read_int(prompt, low=None, high=None):
    while True:
        text = input(prompt).strip()
        try:
            value = int(text)
        except ValueError:
            print("  ! Please enter a whole number.")
            continue
        if low is not None and value < low:
            print(f"  ! Value must be at least {low}.")
            continue
        if high is not None and value > high:
            print(f"  ! Value must be at most {high}.")
            continue
        return value


def read_float(prompt, low=None):
    while True:
        text = input(prompt).strip()
        try:
            value = float(text)
        except ValueError:
            print("  ! Please enter a number.")
            continue
        if low is not None and value < low:
            print(f"  ! Value must be at least {low}.")
            continue
        return value


def choose_medicine(medicines):
    if not medicines:
        print("  No medicines registered yet. Add one first (option 1).")
        return None
    print()
    for i, m in enumerate(medicines, 1):
        print(f"  {i}. {m[0]}  (stock {m[3]}/{m[4]})")
    return read_int("Choose medicine number: ", 1, len(medicines)) - 1


def add_new_medicine():
    name = input("Medicine name: ").strip()
    if not name:
        print("  ! Name cannot be empty.")
        return
    if name.lower() in [s.lower() for s in get_all_medicine_names()]:
        print("  ! That medicine already exists.")
        return
    sell = read_float("Selling price per unit: ", 0.01)
    cost = read_float("Cost price per unit   : ", 0.01)
    if cost > sell:
        print("  (Note: cost price is higher than selling price - you will make a loss.)")
    max_stock = read_int("Maximum shelf capacity (units): ", 1)

    rows = read_csv_rows(MEDICINES_FILE)
    rows.append([name, f"{sell:.2f}", f"{cost:.2f}", '0', str(max_stock)])
    write_csv_rows(MEDICINES_FILE, MEDICINES_HEADER, rows)
    print(f"  + '{name}' added with 0 units in stock.")


def receive_stock():
    medicines = read_csv_rows(MEDICINES_FILE)
    idx = choose_medicine(medicines)
    if idx is None:
        return
    selected = medicines[idx]
    stock, max_stock = int(selected[3]), int(selected[4])
    room = max_stock - stock
    if room <= 0:
        print("  ! Shelf is already full.")
        return

    batch_no = input("Batch number: ").strip()
    if not batch_no:
        print("  ! Batch number cannot be empty.")
        return
    expiry = input("Expiry date (YYYY-MM-DD): ").strip()
    try:
        datetime.strptime(expiry, DATE_FORMAT)
    except ValueError:
        print("  ! Invalid date. Use YYYY-MM-DD, e.g. 2027-03-31.")
        return
    qty = read_int(f"Quantity received (max {room}): ", 1, room)

    batches = read_csv_rows(BATCHES_FILE)
    batches.append([selected[0], batch_no, expiry, str(qty), 'Active'])
    write_csv_rows(BATCHES_FILE, BATCHES_HEADER, batches)

    selected[3] = str(stock + qty)
    write_csv_rows(MEDICINES_FILE, MEDICINES_HEADER, medicines)
    print(f"  + Received {qty} unit(s) of {selected[0]}. Stock is now {selected[3]}.")


def calculate_reorder_allowance(stock, max_stock):
    if max_stock == 0:
        return (0, 0.0, 'No capacity set')
    pct = (stock / max_stock) * 100

    if 100 * stock >= REORDER_PERCENT * max_stock:
        sellable = 0
        temp_stock = stock
        while temp_stock > 0 and 100 * (temp_stock - 1) >= REORDER_PERCENT * max_stock:
            sellable += 1
            temp_stock -= 1
        if sellable == 0:
            return (0, pct, 'At 25% threshold (reorder soon)')
        return (sellable, pct, f'Can sell {sellable} unit(s) before reorder')

    needed = 0
    temp_stock = stock
    while 100 * temp_stock < REORDER_PERCENT * max_stock:
        needed += 1
        temp_stock += 1
    return (-needed, pct, f'LOW STOCK - must receive {needed} unit(s)')


def show_stock_report():
    medicines = read_csv_rows(MEDICINES_FILE)
    if not medicines:
        print("  No medicines registered yet.")
        return
    print(f"\n{'Medicine':<22}{'Stock':>8}{'Max':>7}{'Stock %':>10}  Status")
    print('-' * 80)
    for m in medicines:
        stock, max_stock = int(m[3]), int(m[4])
        _, pct, status = calculate_reorder_allowance(stock, max_stock)
        print(f"{m[0]:<22}{stock:>8}{max_stock:>7}{pct:>9.1f}%  {status}")


def parse_expiry(row):
    try:
        return datetime.strptime(row[2], DATE_FORMAT)
    except ValueError:
        return datetime.max


def get_active_batches_sorted():
    batches = read_csv_rows(BATCHES_FILE)
    active = [row for row in batches if row[4].strip().lower() == 'active']
    active.sort(key=parse_expiry)
    return active


def show_whats_expiring_soon():
    active = get_active_batches_sorted()
    if not active:
        print("  No active batches.")
        return
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    print(f"\n{'Medicine':<22}{'Batch':<12}{'Expiry':<13}{'Qty':>5}  Note")
    print('-' * 80)
    for row in active:
        exp = parse_expiry(row)
        if exp == datetime.max:
            note = 'INVALID DATE - check CSV'
        else:
            days = (exp - today).days
            if days < 0:
                note = f'EXPIRED {-days} day(s) ago'
            elif days <= 30:
                note = f'Expires in {days} day(s) - sell/return soon'
            else:
                note = f'{days} day(s) left'
        print(f"{row[0]:<22}{row[1]:<12}{row[2]:<13}{row[3]:>5}  {note}")


def dispose_batch():
    batches = read_csv_rows(BATCHES_FILE)
    active = [(idx, row) for idx, row in enumerate(batches)
              if row[4].strip().lower() == 'active']
    if not active:
        print("  No active batches to dispose.")
        return
    print()
    for i, (_, row) in enumerate(active, 1):
        print(f"  {i}. {row[0]} | Batch {row[1]} | Exp {row[2]} | Qty {row[3]}")
    choice = read_int("Choose batch to dispose: ", 1, len(active))
    target_idx = active[choice - 1][0]

    med_name = batches[target_idx][0]
    try:
        qty = int(batches[target_idx][3])
    except ValueError:
        qty = 0
    batches[target_idx][4] = 'Disposed'
    write_csv_rows(BATCHES_FILE, BATCHES_HEADER, batches)

    medicines = read_csv_rows(MEDICINES_FILE)
    for m in medicines:
        if m[0].lower() == med_name.lower():
            m[3] = str(max(0, int(m[3]) - qty))
            break
    write_csv_rows(MEDICINES_FILE, MEDICINES_HEADER, medicines)
    print(f"  - Batch disposed. {qty} unit(s) of {med_name} removed from stock.")


def record_sale():
    medicines = read_csv_rows(MEDICINES_FILE)
    idx = choose_medicine(medicines)
    if idx is None:
        return
    selected = medicines[idx]
    stock = int(selected[3])
    if stock == 0:
        print("  ! Out of stock.")
        return
    qty = read_int(f"Quantity to sell (available {stock}): ", 1, stock)

    selected[3] = str(stock - qty)
    write_csv_rows(MEDICINES_FILE, MEDICINES_HEADER, medicines)

    sales = read_csv_rows(SALES_FILE)
    sales.append([selected[0], datetime.now().strftime(DATE_FORMAT), str(qty)])
    write_csv_rows(SALES_FILE, SALES_HEADER, sales)

    total = qty * float(selected[1])
    print(f"  + Sold {qty} x {selected[0]}  =  Rs. {total:.2f}")
    _, _, status = calculate_reorder_allowance(stock - qty, int(selected[4]))
    if status.startswith('LOW') or status.startswith('At 25%'):
        print(f"  ! Stock alert: {status}")


def show_all_sales():
    sales = read_csv_rows(SALES_FILE)
    if not sales:
        print("  No sales recorded yet.")
        return
    grouped = {}
    for name, sale_date, qty in ((r[0], r[1], r[2]) for r in sales):
        try:
            q = int(qty)
        except ValueError:
            continue
        grouped.setdefault(name, []).append((sale_date, q))

    for name, entries in grouped.items():
        total = sum(q for _, q in entries)
        print(f"\n{name}  -  {total} unit(s) sold in {len(entries)} sale(s)")
        for sale_date, q in entries:
            print(f"    {sale_date}   x{q}")


def calculate_sales_stats():
    sub_sales = {}
    for row in read_csv_rows(SALES_FILE):
        try:
            qty = int(row[2])
        except ValueError:
            continue
        key = row[0].lower()
        sub_sales[key] = sub_sales.get(key, 0) + qty

    revenue = profit = 0.0
    units = 0
    per_med = []
    for m in read_csv_rows(MEDICINES_FILE):
        qty = sub_sales.get(m[0].lower(), 0)
        if qty == 0:
            continue
        sell, cost = float(m[1]), float(m[2])
        rev = qty * sell
        prof = qty * (sell - cost)
        revenue += rev
        profit += prof
        units += qty
        per_med.append((m[0], qty, rev, prof))
    return revenue, profit, units, per_med


def show_sales_stats():
    revenue, profit, units, per_med = calculate_sales_stats()
    if not per_med:
        print("  No sales to report yet.")
        return
    print(f"\n{'Medicine':<22}{'Units':>7}{'Revenue':>12}{'Profit':>12}")
    print('-' * 53)
    for name, qty, rev, prof in per_med:
        print(f"{name:<22}{qty:>7}{rev:>12.2f}{prof:>12.2f}")
    print('-' * 53)
    print(f"{'TOTAL':<22}{units:>7}{revenue:>12.2f}{profit:>12.2f}")
    margin = (profit / revenue * 100) if revenue else 0.0
    print(f"Overall profit margin: {margin:.1f}%")
    print("(Revenue uses each medicine's current selling/cost price.)")


def medicine_deep_dive():
    medicines = read_csv_rows(MEDICINES_FILE)
    idx = choose_medicine(medicines)
    if idx is None:
        return
    m = medicines[idx]
    name = m[0]
    stock, max_stock = int(m[3]), int(m[4])
    _, pct, status = calculate_reorder_allowance(stock, max_stock)

    print(f"\n=== {name} ===")
    print(f"Price: Rs. {float(m[1]):.2f} (cost Rs. {float(m[2]):.2f})")
    print(f"Stock: {stock}/{max_stock} ({pct:.1f}%) - {status}")

    batches = [r for r in read_csv_rows(BATCHES_FILE)
               if r[0].lower() == name.lower() and r[4].lower() == 'active']
    batches.sort(key=parse_expiry)
    print("Active batches:")
    if batches:
        for r in batches:
            print(f"   Batch {r[1]} | Exp {r[2]} | Qty {r[3]}")
    else:
        print("   none")

    sold = 0
    for r in read_csv_rows(SALES_FILE):
        if r[0].lower() == name.lower():
            try:
                sold += int(r[2])
            except ValueError:
                pass
    print(f"Total units sold: {sold}  |  Revenue: Rs. {sold * float(m[1]):.2f}")


def show_morning_dashboard():
    print("\n========== MORNING DASHBOARD ==========")

    print("\n[Medicines below 25% stock]")
    low = []
    for m in read_csv_rows(MEDICINES_FILE):
        units, pct, status = calculate_reorder_allowance(int(m[3]), int(m[4]))
        if units < 0:
            low.append((m[0], pct, -units))
    if low:
        for name, pct, need in low:
            print(f"  ! {name}: {pct:.1f}% - order at least {need} unit(s)")
    else:
        print("  All medicines are above the reorder level.")

    print("\n[3 nearest expiry dates]")
    pending = get_active_batches_sorted()
    if pending:
        for row in pending[:3]:
            print(f"  {row[2]}  {row[0]}  (Batch {row[1]}, Qty {row[3]})")
    else:
        print("  No active batches.")

    revenue, profit, units, _ = calculate_sales_stats()
    print(f"\n[Sales so far] {units} unit(s) | Revenue Rs. {revenue:.2f} "
          f"| Profit Rs. {profit:.2f}")


def print_menu():
    print("""
================ MEDICAL STORE MANAGER ================
  1. Add new medicine
  2. Receive stock (new batch)
  3. Record a sale
  4. Stock level report
  5. What's expiring soon
  6. Dispose a batch
  7. View all sales (grouped)
  8. Revenue & profit stats
  9. Medicine deep dive
 10. Morning dashboard
 11. Exit
=======================================================""")


def main():
    setup_files()
    actions = {
        1: add_new_medicine,
        2: receive_stock,
        3: record_sale,
        4: show_stock_report,
        5: show_whats_expiring_soon,
        6: dispose_batch,
        7: show_all_sales,
        8: show_sales_stats,
        9: medicine_deep_dive,
        10: show_morning_dashboard,
    }
    while True:
        print_menu()
        choice = read_int("Enter choice (1-11): ", 1, 11)
        if choice == 11:
            print("Goodbye!")
            break
        actions[choice]()


if __name__ == '__main__':
    main()
