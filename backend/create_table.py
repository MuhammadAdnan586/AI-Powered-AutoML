from app.database.connection import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS engineered_datasets (
            id INT AUTO_INCREMENT PRIMARY KEY,
            processed_dataset_id INT NOT NULL,
            file_path VARCHAR(1000) NOT NULL,
            target_column VARCHAR(200) NOT NULL,
            fe_config TEXT NULL,
            fe_report TEXT NULL,
            `rows` INT NULL,
            `columns` INT NULL,
            status VARCHAR(50) DEFAULT 'completed',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (processed_dataset_id) REFERENCES processed_datasets(id) ON DELETE CASCADE,
            INDEX ix_engineered_datasets_id (id)
        )
    """))
    conn.commit()
    print("Table created successfully!")