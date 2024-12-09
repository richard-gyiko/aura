import logging

from litellm import completion
import pyarrow as pa

from ._types import SchemaElement, SchemaInfoResponse

# Configure logging
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are an expert in Python programming, specializing in data processing with PyArrow.
Your task is to generate PyArrow schemas info from a plain text description of a schema.
To determine which fields to embed, consider the use of embeddings for semantic search capabilities.

### Supported Data Types:
- `string` (PyArrow: `pyarrow.string()`)
- `int32` (PyArrow: `pyarrow.int32()`)
- `int64` (PyArrow: `pyarrow.int64()`)
- `float32` (PyArrow: `pyarrow.float32()`)
- `float64` (PyArrow: `pyarrow.float64()`)
- `bool` (PyArrow: `pyarrow.bool_()`)
- Timestamps:
  - `timestamp[s]` (PyArrow: `pyarrow.timestamp('s')`)
  - `timestamp[ms]` (PyArrow: `pyarrow.timestamp('ms')`)
  - `timestamp[us]` (PyArrow: `pyarrow.timestamp('us')`)
  - `timestamp[ns]` (PyArrow: `pyarrow.timestamp('ns')`)
"""


def to_pyarrows_schema(
    schema_elements: list[SchemaElement], vector_size: int
) -> pa.Schema:
    """
    Parses a string representation of a schema and builds a pyarrow.Schema.

    Args:
        schema_str (str): String representation of the schema.
                          Example: "name: string, age: int32, salary: float64"

    Returns:
        pa.Schema: A PyArrow Schema object.
    """
    logger.debug(f"Converting {len(schema_elements)} schema elements to PyArrow schema")
    field_mappings = {
        "string": pa.string(),
        "int32": pa.int32(),
        "int64": pa.int64(),
        "float32": pa.float32(),
        "float64": pa.float64(),
        "bool": pa.bool_(),
        "timestamp[s]": pa.timestamp("s"),
        "timestamp[ms]": pa.timestamp("ms"),
        "timestamp[us]": pa.timestamp("us"),
        "timestamp[ns]": pa.timestamp("ns"),
    }

    fields = []
    for element in schema_elements:
        name = element.field_name
        dtype = element.data_type

        if dtype not in field_mappings:
            logger.error(f"Encountered unsupported data type: {dtype}")
            raise ValueError(f"Unsupported data type: {dtype}")

        logger.debug(f"Adding field: {name} with type: {dtype}")
        fields.append(pa.field(name, field_mappings[dtype]))

    has_embedded = any([element.embedded for element in schema_elements])
    if has_embedded:
        logger.debug(f"Add vector field for embeddings with fixed length {vector_size}")
        fields.append(pa.field("vector", pa.list_(pa.float32(), vector_size)))

    schema = pa.schema(fields)
    logger.debug(f"Created PyArrow schema with {len(fields)} fields: {schema}")
    return schema


def generate_schema_info(schema_description: str, max_retry: int = 3) -> SchemaInfoResponse:
    logger.info(f"Generating schema for description: {schema_description}")
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": schema_description},
    ]

    retry_count = 0
    logger.info(f"Starting schema generation with max_retry={max_retry}")
    logger.debug(f"Initial messages: {messages}")
    while retry_count < max_retry:
        logger.debug(f"Attempt {retry_count + 1}/{max_retry}")
        logger.debug(f"Sending completion request with {len(messages)} messages")
        try:
            response = completion(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0,
                response_format=SchemaInfoResponse,
            )
            logger.debug(f"Received response: {response.choices[0].message.content}")
        except Exception as e:
            logger.error(f"Error during completion request: {str(e)}")
            raise

        schema_info = SchemaInfoResponse.model_validate_json(
            response.choices[0].message.content
        )
        logger.debug(f"Generated schema: {schema_info}")

        # Validate the schema elements
        try:
            arrow_schema = to_pyarrows_schema(
                schema_info.schema_elements, vector_size=1536
            )
            logger.info(f"Successfully generated and validated schema: {arrow_schema}")
            return schema_info
        except ValueError as e:
            logger.warning(
                f"Schema validation failed on attempt {retry_count + 1}: {str(e)}"
            )
            retry_count += 1
            if retry_count >= max_retry:
                error_msg = f"Failed to generate valid schema after {max_retry} attempts. Last error: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Add error feedback for retry
            retry_prompt = (
                f"The previous schema generation failed with error: {str(e)}. "
                "Please generate a new schema using only the supported data types "
                "and ensure all field names and types are valid."
            )
            messages.append(
                {"role": "assistant", "content": response.messages[0].content}
            )
            messages.append({"role": "user", "content": retry_prompt})

    raise ValueError(f"Failed to generate valid schema after {max_retry} attempts")
