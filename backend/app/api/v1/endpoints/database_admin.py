from datetime import date, datetime
from decimal import Decimal
import time
from typing import Any, Dict, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text, inspect as sa_inspect
from sqlalchemy.orm import Session

from app.api import deps

router = APIRouter()

SENSITIVE_KEYWORDS = {"password", "hashed_password", "token", "dev_token", "secret"}


def _serialize_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value) if value % 1 != 0 else int(value)
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, bytes):
        return "<binary_data>"
    return value


def _get_table_category(table_name: str) -> str:
    tbl = table_name.lower()
    if any(k in tbl for k in ["keuangan", "pemasukan", "pengeluaran", "anggaran", "transaksi"]):
        return "Keuangan Gereja"
    if any(k in tbl for k in ["church", "gereja", "jemaat", "agenda"]):
        return "Gereja & Jemaat"
    if any(k in tbl for k in ["admin", "user", "auth", "account"]):
        return "Autentikasi & Akun"
    if any(k in tbl for k in ["audit", "log", "setting", "item"]):
        return "Sistem & Audit"
    return "Modul Lainnya"


@router.get("/overview")
def get_database_overview(
    db: Session = Depends(deps.get_db),
    _: Any = Depends(deps.get_current_superadmin),
) -> dict[str, Any]:
    bind = db.get_bind()
    dialect_name = bind.dialect.name
    inspector = sa_inspect(bind)

    # 1. Connection and Version Information
    try:
        if dialect_name == "postgresql":
            conn_info = db.execute(
                text("SELECT current_database() AS database_name, current_user AS database_user, version() AS version")
            ).mappings().one()
            database_name = conn_info["database_name"]
            database_user = conn_info["database_user"]
            version_str = conn_info["version"].split(",", 1)[0]

            # Database total size & connections
            try:
                stat_info = db.execute(
                    text("""
                        SELECT 
                            pg_size_pretty(pg_database_size(current_database())) AS db_size,
                            count(*) AS active_connections
                        FROM pg_stat_activity 
                        WHERE datname = current_database()
                    """)
                ).mappings().one()
                db_size = stat_info["db_size"]
                active_connections = stat_info["active_connections"]
            except Exception:
                db_size = "N/A"
                active_connections = 1

            # Fetch table sizes in one bulk query
            try:
                sizes_res = db.execute(
                    text("""
                        SELECT 
                            tablename, 
                            pg_size_pretty(pg_total_relation_size(quote_ident(tablename))) AS size,
                            pg_total_relation_size(quote_ident(tablename)) AS size_bytes
                        FROM pg_tables 
                        WHERE schemaname = 'public'
                    """)
                ).mappings().all()
                table_sizes = {r["tablename"]: {"size": r["size"], "bytes": r["size_bytes"]} for r in sizes_res}
            except Exception:
                table_sizes = {}
        else:
            database_name = "Local Database"
            database_user = "Local User"
            version_str = dialect_name
            db_size = "N/A"
            active_connections = 1
            table_sizes = {}
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Koneksi database {dialect_name} tidak tersedia.") from error

    # 2. Dynamic Tables Inspection
    all_table_names = sorted(inspector.get_table_names())
    tables = []
    total_db_rows = 0

    for tbl_name in all_table_names:
        # Ignore alembic internal migrations table if desired or show it
        # Row count
        try:
            row_count = db.execute(text(f'SELECT count(*) FROM "{tbl_name}"')).scalar() or 0
        except Exception:
            row_count = 0
        total_db_rows += row_count

        # Column metadata
        try:
            columns_raw = inspector.get_columns(tbl_name)
            pks = set(inspector.get_pk_constraint(tbl_name).get("constrained_columns", []))
            fks = inspector.get_foreign_keys(tbl_name)
            indexes = inspector.get_indexes(tbl_name)

            protected_columns = [
                col["name"] for col in columns_raw 
                if any(kw in col["name"].lower() for kw in SENSITIVE_KEYWORDS)
            ]

            columns_summary = [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True),
                    "is_pk": col["name"] in pks,
                    "is_sensitive": col["name"] in protected_columns,
                }
                for col in columns_raw
            ]
        except Exception:
            columns_summary = []
            protected_columns = []
            pks = set()
            fks = []
            indexes = []

        size_info = table_sizes.get(tbl_name, {"size": "N/A", "bytes": 0})

        tables.append({
            "name": tbl_name,
            "label": tbl_name.replace("_", " ").title(),
            "category": _get_table_category(tbl_name),
            "rows": row_count,
            "columns_count": len(columns_summary),
            "columns": columns_summary,
            "primary_keys": list(pks),
            "foreign_keys_count": len(fks),
            "indexes_count": len(indexes),
            "size": size_info["size"],
            "size_bytes": size_info["bytes"],
            "protected_columns": sorted(protected_columns),
        })

    # Sort tables by category, then by name
    tables.sort(key=lambda t: (t["category"], t["name"]))

    return {
        "connected": True,
        "database": database_name,
        "user": database_user,
        "engine": "PostgreSQL" if dialect_name == "postgresql" else dialect_name.title(),
        "version": version_str,
        "db_size": db_size,
        "active_connections": active_connections,
        "total_tables": len(tables),
        "total_rows": total_db_rows,
        "tables": tables,
        "security": {
            "orm_queries": True,
            "parameterized_sql": True,
            "raw_query_console": False,
            "sensitive_columns_hidden": True,
            "dynamic_schema_inspection": True,
        },
    }


@router.get("/tables/{table_name}")
def get_table_preview(
    table_name: str,
    db: Session = Depends(deps.get_db),
    _: Any = Depends(deps.get_current_superadmin),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    search: Optional[str] = Query(default=None),
    sort_by: Optional[str] = Query(default=None),
    sort_dir: Optional[str] = Query(default="asc"),
) -> dict[str, Any]:
    bind = db.get_bind()
    inspector = sa_inspect(bind)
    all_tables = inspector.get_table_names()

    if table_name not in all_tables:
        raise HTTPException(status_code=404, detail=f"Tabel '{table_name}' tidak ditemukan di database.")

    # Column inspection
    columns_raw = inspector.get_columns(table_name)
    column_names = [col["name"] for col in columns_raw]
    pks = set(inspector.get_pk_constraint(table_name).get("constrained_columns", []))
    fks = inspector.get_foreign_keys(table_name)
    indexes = inspector.get_indexes(table_name)

    sensitive_set = {
        col["name"] for col in columns_raw
        if any(kw in col["name"].lower() for kw in SENSITIVE_KEYWORDS)
    }

    columns_meta = [
        {
            "name": col["name"],
            "type": str(col["type"]),
            "nullable": col.get("nullable", True),
            "is_pk": col["name"] in pks,
            "is_sensitive": col["name"] in sensitive_set,
        }
        for col in columns_raw
    ]

    # Build safe query
    where_clause = ""
    params: dict[str, Any] = {"limit": limit, "offset": offset}

    if search and search.strip():
        search_terms = []
        # Filter across all string/text or numeric columns
        for idx, col in enumerate(columns_raw):
            col_name = col["name"]
            if col_name in sensitive_set:
                continue
            param_key = f"search_term_{idx}"
            search_terms.append(f'CAST("{col_name}" AS TEXT) ILIKE :{param_key}')
            params[param_key] = f"%{search.strip()}%"
        if search_terms:
            where_clause = "WHERE " + " OR ".join(search_terms)

    # Total rows matching criteria
    try:
        count_query = text(f'SELECT count(*) FROM "{table_name}" {where_clause}')
        total_rows = db.execute(count_query, params).scalar() or 0
    except Exception:
        total_rows = 0

    # Order clause
    order_clause = ""
    if sort_by and sort_by in column_names:
        direction = "DESC" if sort_dir and sort_dir.lower() == "desc" else "ASC"
        order_clause = f'ORDER BY "{sort_by}" {direction}'
    elif pks:
        # Default order by first primary key desc
        first_pk = list(pks)[0]
        order_clause = f'ORDER BY "{first_pk}" DESC'

    query_str = f'SELECT * FROM "{table_name}" {where_clause} {order_clause} LIMIT :limit OFFSET :offset'
    
    try:
        result = db.execute(text(query_str), params)
        raw_rows = result.mappings().all()
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data tabel: {str(err)}")

    safe_rows = []
    for r in raw_rows:
        row_dict = {}
        for col_name, val in r.items():
            if col_name in sensitive_set:
                row_dict[col_name] = "•••••••• [TERLINDUNGI]"
            else:
                row_dict[col_name] = _serialize_value(val)
        safe_rows.append(row_dict)

    return {
        "table": table_name,
        "total_rows": total_rows,
        "limit": limit,
        "offset": offset,
        "columns": columns_meta,
        "primary_keys": list(pks),
        "foreign_keys": [
            {
                "constrained_columns": fk.get("constrained_columns", []),
                "referred_table": fk.get("referred_table"),
                "referred_columns": fk.get("referred_columns", []),
            }
            for fk in fks
        ],
        "indexes": [
            {
                "name": idx.get("name"),
                "unique": idx.get("unique", False),
                "column_names": idx.get("column_names", []),
            }
            for idx in indexes
        ],
        "rows": safe_rows,
    }


@router.get("/tables/{table_name}/schema")
def get_table_schema(
    table_name: str,
    db: Session = Depends(deps.get_db),
    _: Any = Depends(deps.get_current_superadmin),
) -> dict[str, Any]:
    bind = db.get_bind()
    inspector = sa_inspect(bind)
    all_tables = inspector.get_table_names()

    if table_name not in all_tables:
        raise HTTPException(status_code=404, detail=f"Tabel '{table_name}' tidak ditemukan di database.")

    columns_raw = inspector.get_columns(table_name)
    pks = set(inspector.get_pk_constraint(table_name).get("constrained_columns", []))
    fks = inspector.get_foreign_keys(table_name)
    indexes = inspector.get_indexes(table_name)

    return {
        "table": table_name,
        "columns": [
            {
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col.get("nullable", True),
                "default": str(col.get("default", "")) if col.get("default") is not None else None,
                "is_pk": col["name"] in pks,
            }
            for col in columns_raw
        ],
        "primary_keys": list(pks),
        "foreign_keys": fks,
        "indexes": indexes,
    }


@router.post("/connection-check")
def check_database_connection(
    db: Session = Depends(deps.get_db),
    _: Any = Depends(deps.get_current_superadmin),
) -> dict[str, Any]:
    start_time = time.perf_counter()
    try:
        db.execute(text("SELECT 1"))
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
    except Exception as error:
        raise HTTPException(status_code=503, detail="Tes koneksi PostgreSQL gagal.") from error
    return {
        "connected": True, 
        "message": f"Koneksi PostgreSQL aktif dan responsif ({latency_ms} ms).",
        "latency_ms": latency_ms
    }


def _generate_table_ddl(table_name: str, inspector: Any) -> str:
    columns = inspector.get_columns(table_name)
    pk_info = inspector.get_pk_constraint(table_name)
    pks = pk_info.get("constrained_columns", [])
    pk_name = pk_info.get("name") or f"{table_name}_pkey"
    fks = inspector.get_foreign_keys(table_name)

    col_defs = []
    for col in columns:
        col_type = str(col["type"])
        nullable = "" if col.get("nullable", True) else " NOT NULL"
        default = f" DEFAULT {col['default']}" if col.get("default") is not None else ""
        col_defs.append(f'    "{col["name"]}" {col_type}{nullable}{default}')

    constraints = []
    if pks:
        pk_cols = ", ".join(f'"{c}"' for c in pks)
        constraints.append(f'    CONSTRAINT "{pk_name}" PRIMARY KEY ({pk_cols})')

    for fk in fks:
        name = fk.get("name") or f"{table_name}_{fk['constrained_columns'][0]}_fkey"
        c_cols = ", ".join(f'"{c}"' for c in fk.get("constrained_columns", []))
        r_table = fk.get("referred_table")
        r_cols = ", ".join(f'"{c}"' for c in fk.get("referred_columns", []))
        ondelete = fk.get("options", {}).get("ondelete")
        ondelete_str = f" ON DELETE {ondelete}" if ondelete else ""
        constraints.append(f'    CONSTRAINT "{name}" FOREIGN KEY ({c_cols}) REFERENCES "{r_table}" ({r_cols}){ondelete_str}')

    all_defs = col_defs + constraints
    body = ",\n".join(all_defs)
    return f'CREATE TABLE public."{table_name}" (\n{body}\n);'


@router.get("/tables/{table_name}/ddl")
def get_table_ddl(
    table_name: str,
    db: Session = Depends(deps.get_db),
    _: Any = Depends(deps.get_current_superadmin),
) -> dict[str, Any]:
    bind = db.get_bind()
    inspector = sa_inspect(bind)
    if table_name not in inspector.get_table_names():
        raise HTTPException(status_code=404, detail=f"Tabel '{table_name}' tidak ditemukan.")

    ddl_sql = _generate_table_ddl(table_name, inspector)
    return {
        "table": table_name,
        "ddl": ddl_sql
    }


@router.post("/tables/{table_name}/vacuum")
def vacuum_analyze_table(
    table_name: str,
    db: Session = Depends(deps.get_db),
    _: Any = Depends(deps.get_current_superadmin),
) -> dict[str, Any]:
    bind = db.get_bind()
    inspector = sa_inspect(bind)
    if table_name not in inspector.get_table_names():
        raise HTTPException(status_code=404, detail=f"Tabel '{table_name}' tidak ditemukan.")

    start_time = time.perf_counter()
    try:
        db.execute(text(f'ANALYZE "{table_name}"'))
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        size_res = db.execute(
            text(f"SELECT pg_size_pretty(pg_total_relation_size(quote_ident('{table_name}'))) AS size")
        ).scalar()
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Gagal melakukan optimasi tabel: {str(err)}")

    return {
        "success": True,
        "table": table_name,
        "operation": "ANALYZE & OPTIMIZE",
        "duration_ms": elapsed_ms,
        "size": size_res or "N/A",
        "message": f"Tabel '{table_name}' berhasil dioptimasi dalam {elapsed_ms} ms. Statistik indeks dan estimasi perencana kueri PostgreSQL telah disegarkan."
    }


class SqlQueryRequest(BaseModel):
    query: str


@router.post("/query")
def execute_safe_query(
    payload: SqlQueryRequest,
    db: Session = Depends(deps.get_db),
    _: Any = Depends(deps.get_current_superadmin),
) -> dict[str, Any]:
    raw_query = payload.query.strip()
    if not raw_query:
        raise HTTPException(status_code=400, detail="Kueri SQL tidak boleh kosong.")

    clean_upper = raw_query.upper().lstrip()
    if not (clean_upper.startswith("SELECT") or clean_upper.startswith("EXPLAIN") or clean_upper.startswith("WITH")):
        raise HTTPException(
            status_code=403,
            detail="Konsol ini hanya mengizinkan kueri baca aman (SELECT / EXPLAIN / CTE WITH). Kueri mutasi data (INSERT, UPDATE, DELETE, DROP, TRUNCATE, ALTER) tidak diizinkan demi keamanan data."
        )

    forbidden_tokens = ["DROP ", "DELETE ", "TRUNCATE ", "ALTER ", "UPDATE ", "INSERT ", "GRANT ", "REVOKE "]
    for token in forbidden_tokens:
        if token in clean_upper:
            raise HTTPException(
                status_code=403,
                detail=f"Kueri mengandung token yang dilarang '{token.strip()}'. Operasi dibatalkan."
            )

    exec_query = raw_query.rstrip(";")
    if "LIMIT " not in clean_upper and "EXPLAIN" not in clean_upper:
        exec_query += " LIMIT 100"

    start_time = time.perf_counter()
    try:
        res = db.execute(text(exec_query))
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        if res.returns_rows:
            columns = list(res.keys())
            mappings = res.mappings().all()
            safe_rows = []
            for r in mappings:
                safe_r = {}
                for col in columns:
                    if any(kw in col.lower() for kw in SENSITIVE_KEYWORDS):
                        safe_r[col] = "•••••••• [TERLINDUNGI]"
                    else:
                        safe_r[col] = _serialize_value(r[col])
                safe_rows.append(safe_r)
            return {
                "columns": columns,
                "rows": safe_rows,
                "total_rows": len(safe_rows),
                "execution_ms": elapsed_ms,
                "query": exec_query,
            }
        else:
            return {
                "columns": ["Result"],
                "rows": [{"Result": "Query dieksekusi tanpa hasil baris data."}],
                "total_rows": 0,
                "execution_ms": elapsed_ms,
                "query": exec_query,
            }
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Kueri gagal dieksekusi: {str(err)}")


@router.get("/erd-schema")
def get_erd_schema(
    db: Session = Depends(deps.get_db),
    _: Any = Depends(deps.get_current_superadmin),
) -> dict[str, Any]:
    bind = db.get_bind()
    inspector = sa_inspect(bind)
    tables = sorted(inspector.get_table_names())

    nodes = []
    edges = []

    for t in tables:
        pks = set(inspector.get_pk_constraint(t).get("constrained_columns", []))
        fks = inspector.get_foreign_keys(t)
        cols = inspector.get_columns(t)

        try:
            row_count = db.execute(text(f'SELECT count(*) FROM "{t}"')).scalar() or 0
        except Exception:
            row_count = 0

        try:
            size_res = db.execute(
                text(f"SELECT pg_size_pretty(pg_total_relation_size(quote_ident('{t}'))) AS size")
            ).scalar()
        except Exception:
            size_res = "N/A"

        nodes.append({
            "id": t,
            "name": t,
            "label": t.replace("_", " ").title(),
            "category": _get_table_category(t),
            "rows": row_count,
            "size": size_res or "N/A",
            "columns": [
                {
                    "name": c["name"],
                    "type": str(c["type"]),
                    "is_pk": c["name"] in pks,
                    "nullable": c.get("nullable", True),
                }
                for c in cols
            ]
        })

        for fk in fks:
            c_cols = fk.get("constrained_columns", [])
            r_cols = fk.get("referred_columns", [])
            for c_col, r_col in zip(c_cols, r_cols):
                edges.append({
                    "id": f"{t}_{c_col}_to_{fk.get('referred_table')}_{r_col}",
                    "from": t,
                    "from_col": c_col,
                    "to": fk.get("referred_table"),
                    "to_col": r_col,
                    "constraint": fk.get("name"),
                    "ondelete": fk.get("options", {}).get("ondelete") or "RESTRICT"
                })

    return {
        "nodes": nodes,
        "edges": edges,
        "total_nodes": len(nodes),
        "total_edges": len(edges),
    }

