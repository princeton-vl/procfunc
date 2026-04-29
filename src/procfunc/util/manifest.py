"""Utilities for reading and filtering manifest CSV files."""

import importlib
import logging
from pathlib import Path
from typing import Any, Callable

import pandas as pd

logger = logging.getLogger(__name__)


def module_path():
    return Path(__file__).parent.parent


def filter_manifest(
    manifest: pd.DataFrame,
    filter: dict[str, str] | None = None,
    exclude: dict[str, list[str]] | None = None,
    require_nonempty: list[str] | None = None,
    min_entries: int | None = None,
) -> pd.DataFrame:
    if filter is None:
        filter = {}
    if exclude is None:
        exclude = {}
    if require_nonempty is None:
        require_nonempty = []

    for k, v in filter.items():
        assert k in manifest.columns, (
            f"Filter {k}={v} did not match any columns in {manifest.columns}"
        )

        before_count = len(manifest)
        manifest = manifest.dropna(subset=[k])
        manifest = manifest[manifest[k] == v]
        after_count = len(manifest)
        logger.debug(
            f"Filter {k}={v}: {before_count} -> {after_count} (dropped {before_count - after_count})"
        )

    for column, patterns in exclude.items():
        if not isinstance(patterns, list):
            patterns = [patterns]

        before_count = len(manifest)
        if manifest[column].dtype == "object":
            mask = pd.Series([False] * len(manifest), index=manifest.index)
            for pattern in patterns:
                if isinstance(pattern, str):
                    mask |= manifest[column].str.contains(pattern, na=False)
                else:
                    mask |= manifest[column] == pattern
        else:
            mask = manifest[column].isin(patterns)
        manifest = manifest[~mask]
        after_count = len(manifest)
        logger.debug(
            f"Exclude {column} patterns {patterns}: {before_count} -> {after_count} (dropped {before_count - after_count})"
        )

    if require_nonempty:
        before_count = len(manifest)
        manifest = manifest.dropna(subset=require_nonempty)
        after_count = len(manifest)
        logger.debug(
            f"Require nonempty {require_nonempty}: {before_count} -> {after_count} (dropped {before_count - after_count})"
        )

    if min_entries is not None and len(manifest) < min_entries:
        raise ValueError(
            f"Expected at least {min_entries} entries, got {len(manifest)} "
            f"with {filter=} and {exclude=} and {require_nonempty=}"
        )

    return manifest


def import_item(name: str) -> Any:
    """
    Find and import a function or class by its dotted module path.

    Args:
        name: Dotted module path like "mymodule.generators.objects.funcname"

    Returns:
        The imported function or class

    Raises:
        ModuleNotFoundError: If the module or attribute cannot be found
    """
    *path_parts, item_name = name.split(".")
    try:
        return importlib.import_module("." + item_name, ".".join(path_parts))
    except Exception as e:
        if not isinstance(e, ModuleNotFoundError):
            raise e

    mod = importlib.import_module(".".join(path_parts))
    try:
        return getattr(mod, item_name)
    except AttributeError as e:
        raise AttributeError(
            f"Attribute {item_name} not found in module {mod.__name__}, {dir(mod)=}"
        ) from e


def import_item_iterative(name: str, from_mod: Any | None = None) -> Callable:
    first, *rest = name.split(".")

    if len(rest) == 0:
        assert from_mod is not None, f"No module specified for {name}"
        return getattr(from_mod, name)
    elif from_mod is None:
        mod = importlib.import_module(first)
        return import_item_iterative(".".join(rest), mod)
    else:
        mod = getattr(from_mod, first)
        return import_item_iterative(".".join(rest), mod)
