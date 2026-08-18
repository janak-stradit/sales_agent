"""AccountProductService — Products, Services & Delivery Functional Units (LOB §3.3)."""

import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.database import Base


class AccountProductService(Base):
    __tablename__ = "account_products_services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    lob_id = Column(UUID(as_uuid=True), ForeignKey("account_lobs.id", ondelete="CASCADE"), nullable=False, index=True)

    # Identifiers (LOB §3.3)
    lob_identifier = Column(String(100))
    sub_lob_identifier = Column(String(100))

    # Products (LOB §3.3)
    product_name = Column(String(255))
    product_category = Column(String(100))
    product_description = Column(Text)
    product_parent_entity = Column(String(255))

    # Services (LOB §3.3)
    service_name = Column(String(255))
    service_category = Column(String(100))
    service_description = Column(Text)
    delivery_function = Column(String(255))
    service_parent_entity = Column(String(255))

    # Functional Responsibilities & Operations (LOB §3.3)
    function_name = Column(String(255))
    functional_responsibility = Column(Text)
    supported_product_service = Column(String(255))
    function_parent_entity = Column(String(255))

    # Relational Mappings & Evidence (LOB §3.3)
    entity_to_product_relationship = Column(String(255))
    entity_to_service_relationship = Column(String(255))
    evidence_mapping_statement = Column(Text)
    evidence_backed_mapping_statement = Column(Text)

    # Classification & Validation (LOB §3.3)
    classification = Column(String(100))
    confidence = Column(String(50), default="HIGH")
    source_count = Column(Integer, default=1)
    validation_status = Column(String(50), default="VALIDATED")

    raw_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    account = relationship("Account", back_populates="products_services")
    lob = relationship("AccountLob", back_populates="products_services")

    def __repr__(self):
        return f"<AccountProductService(product='{self.product_name}', service='{self.service_name}')>"
