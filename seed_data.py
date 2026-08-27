"""
Seed script to populate initial sample data for demonstration.
"""
from datetime import date, timedelta
from app.database import SessionLocal, engine, Base
from app.models import Machine, InventoryItem, MaintenanceLog

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(Machine).count() > 0:
            print("[*] Veritabaninda zaten veri mevcut, tohumlama atlandi.")
            return

        print("[*] Ornek veriler yukleniyor...")
        today = date.today()

        # 1. Spare Parts (Inventory)
        parts_data = [
            InventoryItem(
                part_code="YP-101",
                part_name="Siemens Kontaktör 24V DC (3TF30)",
                category="Elektrik",
                stock_quantity=3,  # Critical!
                critical_level=5,
                unit="Adet",
                unit_price=450.0,
                shelf_location="Raf A-1 / K-03",
                notes="CNC panolarında kullanılan ana kontaktör"
            ),
            InventoryItem(
                part_code="YP-102",
                part_name="Omron İndüktif Yaklaşım Sensörü (E2B)",
                category="Sensör",
                stock_quantity=2,  # Critical!
                critical_level=4,
                unit="Adet",
                unit_price=280.0,
                shelf_location="Raf B-2 / K-11",
                notes="Eksen limit sınır sensörü"
            ),
            InventoryItem(
                part_code="YP-103",
                part_name="SKF Bilyalı Rulman 6205-2RSH",
                category="Mekanik",
                stock_quantity=18,  # Healthy
                critical_level=6,
                unit="Adet",
                unit_price=120.0,
                shelf_location="Raf C-1 / K-08",
                notes="Ana mil ve motor yatakları için"
            ),
            InventoryItem(
                part_code="YP-104",
                part_name="Festo Pnömatik Silindir Valfi 5/2",
                category="Pnömatik",
                stock_quantity=1,  # Highly Critical!
                critical_level=3,
                unit="Adet",
                unit_price=850.0,
                shelf_location="Raf D-3 / K-01",
                notes="Pnömatik sıkma ünitesi yön valfi"
            ),
            InventoryItem(
                part_code="YP-105",
                part_name="Mobil DTE 25 Hidrolik Yağ (20L)",
                category="Hidrolik",
                stock_quantity=5,  # Healthy
                critical_level=2,
                unit="Teneke",
                unit_price=1650.0,
                shelf_location="Depo Yağ Alanı - Y-02",
                notes="Pres hidrolik güç ünitesi yağı"
            ),
            InventoryItem(
                part_code="YP-106",
                part_name="Optibelt V-Kayış SPA 1250",
                category="Mekanik",
                stock_quantity=12,  # Healthy
                critical_level=4,
                unit="Adet",
                unit_price=95.0,
                shelf_location="Raf C-2 / K-04",
                notes="Kompresör ve tahrik motorları için"
            ),
            InventoryItem(
                part_code="YP-107",
                part_name="Schneider Termik Manyetik Şalter 16A",
                category="Elektrik",
                stock_quantity=2,  # Critical!
                critical_level=3,
                unit="Adet",
                unit_price=320.0,
                shelf_location="Raf A-2 / K-05",
                notes="Motor koruma şalteri"
            )
        ]
        db.add_all(parts_data)
        db.commit()

        # 2. Machines
        machines_data = [
            Machine(
                machine_code="M-101",
                name="CNC Dik İşleme Merkezi 1",
                model="Mazak VTC-800/30SR",
                serial_number="MZ-2021-884",
                location="Talaşlı İmalat - Hat 1",
                last_maintenance_date=today - timedelta(days=28),
                maintenance_interval_days=30,
                next_maintenance_date=today + timedelta(days=2),  # Upcoming in 2 days!
                status="Aktif",
                notes="5 Eksen freze tezgahı. Spindle soğutma sıvısı seviyesi düzenli izlenmeli."
            ),
            Machine(
                machine_code="M-102",
                name="CNC Torna Tezgahı",
                model="Doosan Puma GT2100",
                serial_number="DS-2019-142",
                location="Talaşlı İmalat - Hat 2",
                last_maintenance_date=today - timedelta(days=48),
                maintenance_interval_days=45,
                next_maintenance_date=today - timedelta(days=3),  # Overdue by 3 days!
                status="Aktif",
                notes="Ayna hidrolik basıncı ve taret indeksleme kontrolü yapılacak."
            ),
            Machine(
                machine_code="M-103",
                name="Hidrolik Derin Çekme Presi (200 Ton)",
                model="Hursan HDP-200",
                serial_number="HR-2018-095",
                location="Pres Atölyesi - Hat A",
                last_maintenance_date=today - timedelta(days=15),
                maintenance_interval_days=60,
                next_maintenance_date=today + timedelta(days=45),  # OK
                status="Aktif",
                notes="Ana keçe takımı ve oransal valfler 6 ay önce yenilendi."
            ),
            Machine(
                machine_code="M-104",
                name="Vidalı Hava Kompresörü",
                model="Atlas Copco GA37+",
                serial_number="AC-2022-771",
                location="Kompresör Dairesi",
                last_maintenance_date=today - timedelta(days=86),
                maintenance_interval_days=90,
                next_maintenance_date=today + timedelta(days=4),  # Upcoming in 4 days!
                status="Aktif",
                notes="Hava-yağ separatör filtresi ve emiş valfi temizliği."
            ),
            Machine(
                machine_code="M-105",
                name="Fiber Lazer Kesim Tezgahı (4kW)",
                model="Bystronic BySmart 3015",
                serial_number="BY-2023-310",
                location="Sac İşleme Bölümü",
                last_maintenance_date=today - timedelta(days=5),
                maintenance_interval_days=30,
                next_maintenance_date=today + timedelta(days=25),  # OK
                status="Aktif",
                notes="Optik koruyucu cam ve nozul merkezleme kontrolü yapıldı."
            )
        ]
        db.add_all(machines_data)
        db.commit()

        # 3. Initial Maintenance Logs
        m1 = db.query(Machine).filter(Machine.machine_code == "M-101").first()
        m3 = db.query(Machine).filter(Machine.machine_code == "M-103").first()
        m5 = db.query(Machine).filter(Machine.machine_code == "M-105").first()
        p3 = db.query(InventoryItem).filter(InventoryItem.part_code == "YP-103").first()
        p5 = db.query(InventoryItem).filter(InventoryItem.part_code == "YP-105").first()

        logs_data = [
            MaintenanceLog(
                machine_id=m1.id,
                part_id=p3.id,
                quantity_used=2,
                maintenance_date=today - timedelta(days=28),
                maintenance_type="Periyodik Bakım",
                technician="Ahmet Usta",
                description="Eksen kızak yağlaması yapıldı, aşınan 2 adet rulman yenisiyle değiştirildi.",
                labor_hours=2.5,
                cost=240.0
            ),
            MaintenanceLog(
                machine_id=m3.id,
                part_id=p5.id,
                quantity_used=1,
                maintenance_date=today - timedelta(days=15),
                maintenance_type="Periyodik Bakım",
                technician="Mehmet Demir",
                description="Hidrolik tank yağı takviyesi yapıldı, filtreler temizlendi, basınç testi 195 bar olarak doğrulandı.",
                labor_hours=3.0,
                cost=1650.0
            ),
            MaintenanceLog(
                machine_id=m5.id,
                part_id=None,
                quantity_used=0,
                maintenance_date=today - timedelta(days=5),
                maintenance_type="Önleyici Bakım",
                technician="Kemal Yıldız",
                description="Lazer kesim kafası koruyucu cam temizliği ve chiller su sıcaklığı kalibrasyonu yapıldı.",
                labor_hours=1.0,
                cost=0.0
            )
        ]
        db.add_all(logs_data)
        db.commit()

        print("[*] Ornek veriler basariyla yuklendi!")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
