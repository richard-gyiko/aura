import lancedb

from ._types import SchemaInfo

DB_PATH = "./.lancedb"


class LanceDbTool:
    def _get_db(self) -> lancedb.db.DBConnection:
        return lancedb.connect(DB_PATH)

    def open_table(self, table_name) -> lancedb.db.Table:
        return self._get_db().open_table(table_name)

    def table_exists(self, table_name) -> bool:
        return table_name in self._get_db().table_names()

    def get_schema_info_table(self) -> lancedb.table.Table:
        db = self._get_db()

        if "schema_info" in db.table_names():
            return db.open_table("schema_info")
        else:
            return db.create_table("schema_info", schema=SchemaInfo)

    def get_schema_info(self, table_name: str) -> SchemaInfo | None:
        schema_table = self.get_schema_info_table()
        results = (
            schema_table.search()
            .where(f"table_name = '{table_name}'", prefilter=True)
            .limit(1)
            .to_pydantic(SchemaInfo)
        )
        return results[0] if results else None
