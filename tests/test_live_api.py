import urllib.request
import json

def test_live_api():
    base_url = 'http://127.0.0.1:8000'

    # 1. Test HTML
    html = urllib.request.urlopen(f'{base_url}/').read().decode('utf-8')
    assert 'Stok ve Makine' in html
    print('[SUCCESS] HTML Dashboard rendered successfully.')

    # 2. Test System Info
    sys_info = json.loads(urllib.request.urlopen(f'{base_url}/api/system-info').read().decode('utf-8'))
    print(f'[SUCCESS] System Info: Local IP = {sys_info.get("local_ip")}, LAN URL = {sys_info.get("lan_url")}')

    # 3. Test Dashboard Summary
    summary = json.loads(urllib.request.urlopen(f'{base_url}/api/dashboard/summary').read().decode('utf-8'))
    print(f'[SUCCESS] Dashboard KPIs: Machines = {summary["kpis"]["total_machines"]}, Critical Parts = {summary["kpis"]["critical_parts_count"]}, Upcoming = {len(summary["upcoming_maintenances"])}')

    # 4. Test Machines API
    machines = json.loads(urllib.request.urlopen(f'{base_url}/api/machines').read().decode('utf-8'))
    print(f'[SUCCESS] Machines Count = {len(machines)}')

    # 5. Test Inventory API
    inventory = json.loads(urllib.request.urlopen(f'{base_url}/api/inventory').read().decode('utf-8'))
    print(f'[SUCCESS] Inventory Items Count = {len(inventory)}')

    # 6. Test Creating Maintenance Log & Automatic Stock Deduction
    part_before = next(p for p in inventory if p['part_code'] == 'YP-103')
    stock_before = part_before['stock_quantity']
    machine_target = machines[0]

    req_data = json.dumps({
        'machine_id': machine_target['id'],
        'part_id': part_before['id'],
        'quantity_used': 2,
        'maintenance_date': '2026-08-25',
        'maintenance_type': 'Periyodik Bakım',
        'technician': 'Sistem Testi',
        'description': 'Otomatik stok dusme entegrasyon testi',
        'labor_hours': 1.5,
        'cost': 240.0
    }).encode('utf-8')

    req = urllib.request.Request(f'{base_url}/api/maintenance', data=req_data, headers={'Content-Type': 'application/json'})
    resp = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    print(f'[SUCCESS] Maintenance Log Created: ID = {resp["id"]}, Machine = {resp["machine_name"]}')

    # Verify stock dropped by 2
    inventory_after = json.loads(urllib.request.urlopen(f'{base_url}/api/inventory').read().decode('utf-8'))
    part_after = next(p for p in inventory_after if p['part_code'] == 'YP-103')
    assert part_after['stock_quantity'] == stock_before - 2, f'Expected {stock_before-2}, got {part_after["stock_quantity"]}'
    print(f'[SUCCESS] AUTOMATIC STOCK DEDUCTION VERIFIED: Part {part_before["part_name"]} went from {stock_before} to {part_after["stock_quantity"]}')

if __name__ == '__main__':
    test_live_api()
