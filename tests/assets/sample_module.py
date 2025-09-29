from exp_platform_cli.models import DataModelRow


def process_row(**kwargs) -> DataModelRow:
    row = kwargs.get("row") or kwargs.get("data_model_row")
    if row is None:
        raise ValueError("DataModelRow instance required")
    row.data_output = {"echo": row.data_input}
    return row
