from pymilvus import FieldSchema, CollectionSchema, DataType

# https://www.youtube.com/watch?v=IgJdrGiB5ZY

DIMENSION=384

fields = {
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True)
    
}

