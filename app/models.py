from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    machine_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    model = Column(String(100), nullable=True)
    serial_number = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    last_maintenance_date = Column(Date, nullable=True)
    maintenance_interval_days = Column(Integer, default=30, nullable=False)
    next_maintenance_date = Column(Date, nullable=True, index=True)
    status = Column(String(30), default="Aktif", nullable=False)  # Aktif, Bakımda, Arızalı, Pasif
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    maintenance_logs = relationship("MaintenanceLog", back_populates="machine", cascade="all, delete-orphan", order_by="desc(MaintenanceLog.maintenance_date)")


class InventoryItem(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    part_code = Column(String(50), unique=True, index=True, nullable=False)
    part_name = Column(String(150), nullable=False)
    category = Column(String(50), default="Genel", nullable=False)  # Elektrik, Mekanik, Pnömatik, Hidrolik, vb.
    stock_quantity = Column(Integer, default=0, nullable=False)
    critical_level = Column(Integer, default=5, nullable=False)
    unit = Column(String(20), default="Adet", nullable=False)
    unit_price = Column(Float, default=0.0, nullable=False)
    shelf_location = Column(String(50), nullable=True)  # Raf / Kutu No
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    maintenance_logs = relationship("MaintenanceLog", back_populates="part")


class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    machine_id = Column(Integer, ForeignKey("machines.id", ondelete="CASCADE"), nullable=False, index=True)
    part_id = Column(Integer, ForeignKey("inventory.id", ondelete="SET NULL"), nullable=True, index=True)
    quantity_used = Column(Integer, default=0, nullable=False)
    maintenance_date = Column(Date, default=date.today, nullable=False, index=True)
    maintenance_type = Column(String(50), default="Periyodik Bakım", nullable=False)  # Periyodik Bakım, Arıza Onarım, Önleyici Bakım
    technician = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    labor_hours = Column(Float, default=1.0, nullable=True)
    cost = Column(Float, default=0.0, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    machine = relationship("Machine", back_populates="maintenance_logs")
    part = relationship("InventoryItem", back_populates="maintenance_logs")
