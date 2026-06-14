import pytest

from procfunc.util import bpy_data


@pytest.fixture(autouse=True)
def _remove_created_bpy_data():
    with bpy_data.removing_new_datablocks():
        yield
