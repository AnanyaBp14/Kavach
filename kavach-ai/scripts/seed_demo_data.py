import os
import uuid
import json
import random
from datetime import datetime, timedelta
import psycopg
from neo4j import GraphDatabase
from minio import Minio
from kafka import KafkaProducer

# ------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------
PG_URL = os.getenv("DATABASE_URL", "postgresql://kavach_user:kavach_pass@localhost:5432/kavach_db")
GEO_URL = os.getenv("GEO_URL", "postgresql://kavach_user:kavach_pass@localhost:5433/kavach_geo")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "kavach_graph_pass")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_USER = os.getenv("MINIO_ROOT_USER", "kavach_admin")
MINIO_PASS = os.getenv("MINIO_ROOT_PASSWORD", "kavach_minio_pass")

# High risk districts
HIGH_RISK_DISTRICTS = [
    {"name": "Jamtara, JH", "lat": 23.9667, "lon": 86.8000, "weight": 40},
    {"name": "Mewat, HR", "lat": 28.0000, "lon": 77.0000, "weight": 35},
    {"name": "Bharatpur, RJ", "lat": 27.2167, "lon": 77.4833, "weight": 20},
    {"name": "Isolated, AP", "lat": 16.5062, "lon": 80.6480, "weight": 5}
]

def main():
    print("--- KAVACH AI: Demo Data Seeder ---")
    
    # 1. Init Connections
    print("Connecting to PostgreSQL (Core)...")
    core_conn = psycopg.connect(PG_URL, autocommit=True)
    
    print("Connecting to PostgreSQL (Geo)...")
    geo_conn = psycopg.connect(GEO_URL, autocommit=True)
    
    print("Connecting to Neo4j...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    
    print("Connecting to Kafka...")
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    print("Connecting to MinIO...")
    minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_USER, secret_key=MINIO_PASS, secure=False)
    if not minio_client.bucket_exists("kavach-evidence"):
        minio_client.make_bucket("kavach-evidence")

    # 2. Clear previous demo data
    print("Clearing old graph data...")
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

    # 3. Seed Story: Fraud Ring Alpha (UPI Fraud in Jamtara)
    print("Seeding Fraud Ring Alpha (UPI)...")
    ring_alpha_upi = "scammer@ybl"
    ring_alpha_phone = "+91 9876543210"
    
    with driver.session() as session:
        session.run("CREATE (:Entity {id: $id, type: 'UPI', risk: 95})", id=ring_alpha_upi)
        session.run("CREATE (:Entity {id: $id, type: 'PHONE', risk: 90})", id=ring_alpha_phone)
        session.run(
            "MATCH (a {id: $id1}), (b {id: $id2}) CREATE (a)-[:LINKED_TO]->(b)",
            id1=ring_alpha_upi, id2=ring_alpha_phone
        )

    for i in range(25):
        comp_id = f"COMP-A{i:03d}"
        vic_phone = f"+91 8888{random.randint(100000, 999999)}"
        district = random.choices(HIGH_RISK_DISTRICTS, weights=[d['weight'] for d in HIGH_RISK_DISTRICTS])[0]
        
        # Jitter lat/lon
        lat = district['lat'] + random.uniform(-0.1, 0.1)
        lon = district['lon'] + random.uniform(-0.1, 0.1)
        
        # Add to Core DB
        core_conn.execute("""
            INSERT INTO complaints (id, source, category, text_content, status)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (comp_id, "CITIZEN_PORTAL", "UPI_FRAUD", f"Money deducted to {ring_alpha_upi}", "ACTIVE"))
        
        # Add to Geo DB
        geo_conn.execute("""
            INSERT INTO geo_incidents (complaint_id, district, lat, lon, geom)
            VALUES (%s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
            ON CONFLICT DO NOTHING
        """, (comp_id, district['name'], lat, lon, lon, lat))
        
        # Add to Neo4j
        with driver.session() as session:
            session.run("CREATE (:Entity {id: $id, type: 'COMPLAINT', risk: 50})", id=comp_id)
            session.run("CREATE (:Entity {id: $id, type: 'PHONE', risk: 10})", id=vic_phone)
            session.run("MATCH (a {id: $id1}), (b {id: $id2}) CREATE (a)-[:FILED_BY]->(b)", id1=comp_id, id2=vic_phone)
            session.run("MATCH (a {id: $id1}), (b {id: $id2}) CREATE (a)-[:MENTIONS]->(b)", id1=comp_id, id2=ring_alpha_upi)

    # 4. Seed Story: Fraud Ring Beta (Digital Arrest in Mewat)
    print("Seeding Fraud Ring Beta (Digital Arrest)...")
    ring_beta_bank = "HDFC-449281"
    
    with driver.session() as session:
        session.run("CREATE (:Entity {id: $id, type: 'BANK_ACCOUNT', risk: 99})", id=ring_beta_bank)

    for i in range(15):
        comp_id = f"COMP-B{i:03d}"
        district = next(d for d in HIGH_RISK_DISTRICTS if d['name'] == "Mewat, HR")
        lat = district['lat'] + random.uniform(-0.05, 0.05)
        lon = district['lon'] + random.uniform(-0.05, 0.05)
        
        core_conn.execute("""
            INSERT INTO complaints (id, source, category, text_content, status)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (comp_id, "POLICE_PORTAL", "DIGITAL_ARREST", f"Fake customs officer asked for transfer to {ring_beta_bank}", "ACTIVE"))
        
        geo_conn.execute("""
            INSERT INTO geo_incidents (complaint_id, district, lat, lon, geom)
            VALUES (%s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
            ON CONFLICT DO NOTHING
        """, (comp_id, district['name'], lat, lon, lon, lat))

        with driver.session() as session:
            session.run("CREATE (:Entity {id: $id, type: 'COMPLAINT', risk: 80})", id=comp_id)
            session.run("MATCH (a {id: $id1}), (b {id: $id2}) CREATE (a)-[:TRANSFERRED_TO]->(b)", id1=comp_id, id2=ring_beta_bank)

    print("Data seeded successfully!")

if __name__ == "__main__":
    main()
