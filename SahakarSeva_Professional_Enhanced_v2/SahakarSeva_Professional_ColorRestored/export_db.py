import mysql.connector
import os
from datetime import datetime, date
from decimal import Decimal

def export_database():
    print("[Dump] Connecting to MySQL...")
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="contractor_erp_db",
        charset="utf8",
        use_pure=True
    )
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"[Dump] Found {len(tables)} tables: {tables}")

    sql_lines = [
        "-- ============================================================================",
        "-- SahakarSeva Cooperative Services - Database Backup Dump",
        f"-- Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"-- Database: contractor_erp_db",
        f"-- Total Tables: {len(tables)}",
        "-- ============================================================================",
        "",
        "SET FOREIGN_KEY_CHECKS=0;",
        "SET SQL_MODE = \"NO_AUTO_VALUE_ON_ZERO\";",
        "START TRANSACTION;",
        "SET time_zone = \"+00:00\";",
        ""
    ]

    def format_val(v):
        if v is None:
            return "NULL"
        if isinstance(v, bool):
            return "1" if v else "0"
        if isinstance(v, (int, float, Decimal)):
            return str(v)
        if isinstance(v, (datetime, date)):
            return f"'{v.strftime('%Y-%m-%d %H:%M:%S' if isinstance(v, datetime) else '%Y-%m-%d')}'"
        if isinstance(v, bytes):
            try:
                v = v.decode('utf-8')
            except Exception:
                return f"0x{v.hex()}"
        
        # String escaping
        s = str(v)
        s = s.replace('\\', '\\\\').replace("'", "\\'").replace('\r', '\\r').replace('\n', '\\n')
        return f"'{s}'"

    for t in tables:
        sql_lines.append(f"-- --------------------------------------------------------")
        sql_lines.append(f"-- Table structure for `{t}`")
        sql_lines.append(f"-- --------------------------------------------------------")
        sql_lines.append(f"DROP TABLE IF EXISTS `{t}`;")
        
        cursor.execute(f"SHOW CREATE TABLE `{t}`;")
        res = cursor.fetchone()
        create_sql = res[1]
        if isinstance(create_sql, (bytes, bytearray)):
            create_sql = create_sql.decode('utf-8')
        
        sql_lines.append(f"{create_sql};")
        sql_lines.append("")

        # Data dump
        cursor.execute(f"SELECT * FROM `{t}`;")
        rows = cursor.fetchall()
        if rows:
            col_names = [f"`{col[0]}`" for col in cursor.description]
            cols_str = ", ".join(col_names)
            sql_lines.append(f"-- Dumping data for table `{t}`")
            sql_lines.append(f"LOCK TABLES `{t}` WRITE;")
            for row in rows:
                vals_str = ", ".join(format_val(val) for val in row)
                sql_lines.append(f"INSERT INTO `{t}` ({cols_str}) VALUES ({vals_str});")
            sql_lines.append("UNLOCK TABLES;")
            sql_lines.append("")

    sql_lines.append("SET FOREIGN_KEY_CHECKS=1;")
    sql_lines.append("COMMIT;")
    sql_lines.append("")

    output_path = os.path.join(os.path.dirname(__file__), 'database_schema_and_data.sql')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_lines))

    cursor.close()
    conn.close()
    print(f"[Dump] Dump completed successfully! Written to {output_path}")

if __name__ == '__main__':
    export_database()
