"""SQLite-backed cursor pagination; use monotonically increasing IDs."""
import sqlite3
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

class ProductIn(BaseModel):
    name: str = Field(min_length=2,max_length=80)
    category: str = Field(min_length=2,max_length=30)
    price_paise: int = Field(ge=0)

def create_app(db_file='catalog.db'):
    app=FastAPI(title='2024 — Keyset Pagination')
    def db():
        conn=sqlite3.connect(db_file,timeout=10)
        conn.row_factory=sqlite3.Row
        return conn
    with db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            category TEXT NOT NULL, price_paise INTEGER NOT NULL
        )""")

    @app.post('/products',status_code=201)
    def add(payload:ProductIn):
        with db() as conn:
            cursor=conn.execute('INSERT INTO products(name,category,price_paise) VALUES (?,?,?)',
                               (payload.name,payload.category,payload.price_paise))
            return {'id':cursor.lastrowid,**payload.model_dump()}

    @app.get('/products')
    def list_products(limit:int=Query(default=5,ge=1,le=50),after:int=Query(default=0,ge=0),
                      category:str | None=None,min_price_paise:int=Query(default=0,ge=0)):
        filters=['id>?','price_paise>=?']
        values=[after,min_price_paise]
        if category:
            filters.append('category=?')
            values.append(category)
        sql='SELECT * FROM products WHERE '+ ' AND '.join(filters) + ' ORDER BY id ASC LIMIT ?'
        with db() as conn:
            rows=conn.execute(sql,(*values,limit+1)).fetchall()
        more=len(rows)>limit
        items=[dict(row) for row in rows[:limit]]
        return {'items':items,'next_cursor':items[-1]['id'] if more and items else None,'has_more':more}

    return app

app=create_app()
