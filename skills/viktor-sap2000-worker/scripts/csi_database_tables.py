"""Database table export helpers for CSI SAP2000 and ETABS worker scripts.

This is an additive helper for SapModel.DatabaseTables workflows. Use it when a
worker should retrieve display tables such as "Element Forces - Frames",
"Joint Displacements", or "Base Reactions" instead of calling each Results.*
method directly.
"""

from __future__ import annotations

from collections.abc import Sequence as RuntimeSequence
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union


TableRecord = Dict[str, Union[str, int, float, None]]


COMMON_TABLE_KEYS: Dict[str, str] = {
    "frame_forces": "Element Forces - Frames",
    "beam_forces": "Element Forces - Beams",
    "joint_displacements": "Joint Displacements",
    "base_reactions": "Base Reactions",
}


COMMON_NUMERIC_COLUMNS: Dict[str, Sequence[str]] = {
    "Element Forces - Frames": ("P", "V2", "V3", "T", "M2", "M3"),
    "Element Forces - Beams": ("P", "V2", "V3", "T", "M2", "M3"),
    "Joint Displacements": ("U1", "U2", "U3", "R1", "R2", "R3"),
    "Base Reactions": ("FX", "FY", "FZ", "MX", "MY", "MZ"),
}


def require_ret_zero(ret: Any, method_name: str) -> None:
    if ret not in (None, 0):
        raise RuntimeError(f"{method_name} failed (ret={ret})")


def _is_sequence(value: Any) -> bool:
    return isinstance(value, RuntimeSequence) and not isinstance(value, (str, bytes, bytearray))


def _result_items(result: Any, method_name: str) -> Tuple[Any, ...]:
    if not _is_sequence(result):
        raise RuntimeError(f"{method_name} returned non-sequence: {type(result)} {result!r}")
    return tuple(result)


def _is_string_sequence(value: Any) -> bool:
    return _is_sequence(value) and all(isinstance(item, str) for item in value)


def _to_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, (str, bytes, bytearray)):
        return [value]
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    try:
        return list(value)
    except TypeError:
        return [value]


def _coerce_scalar(value: Any, numeric: bool = False) -> Union[str, int, float, None]:
    if value is None:
        return None
    if numeric:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
    return str(value)


def get_available_database_tables(model: Any) -> List[str]:
    """Return available CSI database table keys for the open model.

    Input contract: DatabaseTables.GetAvailableTables().
    Output contract: accept tuple/list returns containing one or more string arrays.
    """
    result = model.DatabaseTables.GetAvailableTables()
    result = _result_items(result, "DatabaseTables.GetAvailableTables")

    string_sequences = [value for value in result if _is_string_sequence(value)]
    if not string_sequences:
        return []

    # In CSI wrappers, table keys are normally the first or longest string array.
    return [str(key) for key in max(string_sequences, key=len)]


def set_database_table_output_selection(
    model: Any,
    *,
    load_cases: Optional[Sequence[str]] = None,
    load_combinations: Optional[Sequence[str]] = None,
) -> None:
    """Select cases/combinations for DatabaseTables display output."""
    ret = model.Results.Setup.DeselectAllCasesAndCombosForOutput()
    require_ret_zero(ret, "Results.Setup.DeselectAllCasesAndCombosForOutput")

    if load_cases:
        ret = model.DatabaseTables.SetLoadCasesSelectedForDisplay([str(name) for name in load_cases])
        require_ret_zero(ret, "DatabaseTables.SetLoadCasesSelectedForDisplay")

    if load_combinations:
        ret = model.DatabaseTables.SetLoadCombinationsSelectedForDisplay(
            [str(name) for name in load_combinations]
        )
        require_ret_zero(ret, "DatabaseTables.SetLoadCombinationsSelectedForDisplay")


def call_table_for_display_array(model: Any, table_key: str, group_name: str = "") -> Any:
    """Call GetTableForDisplayArray with keyword and positional fallbacks.

    Input contract: TableKey and GroupName, with field/table OUT arguments
    supplied in the positional fallback for generated comtypes wrappers.
    """
    try:
        return model.DatabaseTables.GetTableForDisplayArray(
            TableKey=str(table_key),
            GroupName=str(group_name),
        )
    except TypeError:
        return model.DatabaseTables.GetTableForDisplayArray(
            str(table_key),
            [],
            str(group_name),
            0,
            [],
            0,
            [],
        )


def parse_table_for_display_array_result(result: Any, table_key: str) -> Tuple[List[str], List[List[Any]]]:
    """Parse common GetTableForDisplayArray return shapes.

    Accepted shapes include the compact form commonly seen in Python wrappers:
    (ret, table_version, fields_keys_included, number_records, table_data)

    and fuller COM-style tuples that also include FieldKeyList.
    List variants of the same shapes are accepted.
    """
    result = _result_items(result, f"DatabaseTables.GetTableForDisplayArray({table_key})")

    ret_candidates = []
    if result and isinstance(result[0], int):
        ret_candidates.append(result[0])
    if result and isinstance(result[-1], int):
        ret_candidates.append(result[-1])
    if 0 in ret_candidates:
        ret = 0
    elif ret_candidates:
        ret = int(ret_candidates[0])
    else:
        ret = 0
    require_ret_zero(ret, f"DatabaseTables.GetTableForDisplayArray({table_key})")

    candidates: List[Tuple[List[str], int, List[Any]]] = []
    for col_index, column_value in enumerate(result):
        if not _is_string_sequence(column_value):
            continue
        columns = [str(column) for column in column_value]
        if not columns:
            continue

        for row_index in range(col_index + 1, len(result)):
            row_value = result[row_index]
            if not isinstance(row_value, int) or row_value < 0:
                continue

            for data_index in range(row_index + 1, len(result)):
                data_value = result[data_index]
                if not _is_sequence(data_value):
                    continue

                flat_data = _to_list(data_value)
                if row_value == 0 and not flat_data:
                    candidates.append((columns, 0, []))
                elif len(flat_data) == row_value * len(columns):
                    candidates.append((columns, int(row_value), flat_data))

    if not candidates:
        raise RuntimeError(
            f"Could not parse DatabaseTables.GetTableForDisplayArray({table_key}) return: {result!r}"
        )

    columns, number_records, flat_data = candidates[-1]
    rows = [
        flat_data[index : index + len(columns)]
        for index in range(0, number_records * len(columns), len(columns))
    ]
    return columns, rows


def records_from_rows(
    columns: Sequence[str],
    rows: Sequence[Sequence[Any]],
    *,
    numeric_columns: Optional[Iterable[str]] = None,
) -> List[TableRecord]:
    numeric = {str(column) for column in numeric_columns or []}
    records: List[TableRecord] = []

    for row in rows:
        record: TableRecord = {}
        for column, value in zip(columns, row):
            column_name = str(column)
            record[column_name] = _coerce_scalar(value, numeric=column_name in numeric)
        records.append(record)

    return records


def get_database_table(
    model: Any,
    table_key: str,
    *,
    group_name: str = "",
    load_cases: Optional[Sequence[str]] = None,
    load_combinations: Optional[Sequence[str]] = None,
    numeric_columns: Optional[Iterable[str]] = None,
    validate_available: bool = True,
) -> Dict[str, Any]:
    """Retrieve one CSI database table as JSON-serializable data."""
    if validate_available:
        available = get_available_database_tables(model)
        if available and table_key not in available:
            raise RuntimeError(
                f"Database table {table_key!r} is not available. "
                f"Available examples: {', '.join(available[:10])}"
            )

    set_database_table_output_selection(
        model,
        load_cases=load_cases,
        load_combinations=load_combinations,
    )
    columns, rows = parse_table_for_display_array_result(
        call_table_for_display_array(model, table_key, group_name),
        table_key,
    )
    numeric = list(numeric_columns or COMMON_NUMERIC_COLUMNS.get(table_key, ()))

    return {
        "table_key": str(table_key),
        "group_name": str(group_name),
        "columns": [str(column) for column in columns],
        "rows": rows,
        "records": records_from_rows(columns, rows, numeric_columns=numeric),
    }


def get_common_database_table(
    model: Any,
    table_name: str,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Retrieve a known table by friendly name.

    Friendly names: frame_forces, beam_forces, joint_displacements,
    base_reactions.
    """
    try:
        table_key = COMMON_TABLE_KEYS[table_name]
    except KeyError as exc:
        raise RuntimeError(f"Unknown common table name: {table_name!r}") from exc

    return get_database_table(model, table_key, **kwargs)


def get_database_tables(model: Any, requests: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Retrieve multiple database tables from request dictionaries."""
    tables: List[Dict[str, Any]] = []
    for request in requests:
        table_key = request.get("table_key") or COMMON_TABLE_KEYS.get(str(request.get("name", "")))
        if not table_key:
            raise RuntimeError(f"Database table request is missing table_key/name: {request!r}")

        tables.append(
            get_database_table(
                model,
                str(table_key),
                group_name=str(request.get("group_name", "")),
                load_cases=request.get("load_cases"),
                load_combinations=request.get("load_combinations"),
                numeric_columns=request.get("numeric_columns"),
                validate_available=bool(request.get("validate_available", True)),
            )
        )
    return tables
