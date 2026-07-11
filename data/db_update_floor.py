"""
Direct DB updater for 28Hse floor & room layout data
"""
import psycopg2
import os

DB_URL = "postgresql://neondb_owner:npg_sVKUOn6P2BlW@ep-ancient-cherry-afmoe2xv-pooler.c-2.us-west-2.aws.neon.tech/neondb?channel_binding=require&sslmode=require"

def run_updates():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    total_updated = 0
    total_statements = 0
    
    # Read all batch files
    import glob
    batch_files = sorted(glob.glob('update_floor_batch_part_*'))
    
    for batch_file in batch_files:
        with open(batch_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        statements = [s.strip() for s in content.split(';') if s.strip()]
        
        for sql in statements:
            cur.execute(sql)
            total_updated += cur.rowcount
            total_statements += 1
        
        print(f"  {batch_file}: {len(statements)} statements")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"\nDone: {total_statements} statements, {total_updated} rows updated")

if __name__ == '__main__':
    run_updates()
