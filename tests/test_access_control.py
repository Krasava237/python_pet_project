from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.users.dependencies import AccessControlService


@pytest.mark.unit
def test_user_can_read_own_profile() -> None:
    access_control = AccessControlService()
    current_user = SimpleNamespace(id=10, role="user")
    target_user = SimpleNamespace(id=10, role="user")

    access_control.ensure_can_read_user(current_user, target_user)


@pytest.mark.unit
def test_regular_user_cannot_read_foreign_profile() -> None:
    access_control = AccessControlService()
    current_user = SimpleNamespace(id=10, role="user")
    target_user = SimpleNamespace(id=11, role="user")

    with pytest.raises(HTTPException) as error:
        access_control.ensure_can_read_user(current_user, target_user)

    assert error.value.status_code == 403


@pytest.mark.unit
def test_admin_can_manage_foreign_pet() -> None:
    access_control = AccessControlService()
    current_user = SimpleNamespace(id=1, role="admin")
    pet = SimpleNamespace(owner_id=22)

    access_control.ensure_pet_permission(current_user, pet, "pets.update_own")
