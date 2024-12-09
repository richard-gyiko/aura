from typing import List

from lancedb.pydantic import LanceModel
import pandas as pd
from pydantic import BaseModel, Field


class SchemaElement(BaseModel):
    field_name: str = Field(..., description="The name of the field in the schema")
    data_type: str = Field(..., description="The data type of the field in the schema")
    embedded: bool = Field(
        description="Whether vector embedding of this filed would be valueable for Retrieval Augmented Generation (RAG) queries",
    )


class SchemaInfo(LanceModel):
    """
    Represents metadata about a table schema in LanceDB.

    This model stores both the schema definition and associated metadata like
    descriptions and embeddings for semantic search capabilities.
    """

    table_name: str = Field(
        description="The unique name identifier for the table in LanceDB"
    )
    description: str = Field(
        description="Human-readable description of the table's purpose and contents"
    )
    schema_elements_str: str = Field(
        description="JSON serialized list of schema elements containing field name, type and embedding flag"
    )

    @property
    def schema_elements(self) -> list[SchemaElement]:
        """
        Converts a JSON string representation of schema elements to a list of SchemaElements.

        Returns:
            list[SchemaElement]: List of SchemaElement objects.
        """
        import json

        elements_data = json.loads(self.schema_elements_str)
        return [SchemaElement(**element) for element in elements_data]

    def create_dataframe(self, data: dict) -> pd.DataFrame:
        """
        Converts a dictionary to a pandas DataFrame using the schema elements for type conversion.

        Args:
            data (dict): Dictionary containing the data to convert

        Returns:
            pd.DataFrame: DataFrame with proper data types based on schema
        """
        # Create initial DataFrame
        df = pd.DataFrame([data])

        # Apply conversions based on schema elements
        for element in self.schema_elements:
            if element.field_name in df.columns:
                # Skip vector field as it's handled separately
                if element.field_name == "vector":
                    continue

                # Handle different data types
                if element.data_type == "int32":
                    df[element.field_name] = pd.to_numeric(
                        df[element.field_name], errors="coerce", downcast="integer"
                    )
                elif element.data_type == "int64":
                    df[element.field_name] = pd.to_numeric(
                        df[element.field_name], errors="coerce"
                    )
                elif element.data_type in ["float32", "float64"]:
                    df[element.field_name] = pd.to_numeric(
                        df[element.field_name], errors="coerce"
                    )
                elif element.data_type.startswith("timestamp"):
                    # Convert to millisecond precision for LanceDB timestamp[ms] type
                    df[element.field_name] = pd.to_datetime(
                        df[element.field_name], errors="coerce"
                    ).astype("datetime64[ms]")
                elif element.data_type == "bool":
                    df[element.field_name] = df[element.field_name].astype("bool")
                elif element.data_type == "string":
                    df[element.field_name] = df[element.field_name].astype("string")

        return df

    @staticmethod
    def schema_elements_to_str(schema_elements: list[SchemaElement]) -> str:
        """
        Converts a list of SchemaElements to a JSON string representation.

        Args:
            schema_elements (list[SchemaElement]): List of SchemaElement objects.

        Returns:
            str: JSON string representation of schema elements.
        """
        import json

        elements_data = [element.model_dump() for element in schema_elements]
        return json.dumps(elements_data)


class SchemaInfoResponse(BaseModel):
    table_name: str = Field(
        description="The unique name identifier for the table in LanceDB"
    )
    description: str = Field(
        description="Human-readable description of the table's purpose and contents"
    )
    schema_elements: List[SchemaElement] = Field(
        description="Fields in the table schema in the format 'name: type, name: type'"
    )

    def to_schema_info(self) -> SchemaInfo:
        return SchemaInfo(
            table_name=self.table_name,
            description=self.description,
            schema_elements_str=SchemaInfo.schema_elements_to_str(self.schema_elements),
        )
