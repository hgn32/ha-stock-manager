from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import StockManagerCoordinator, _API_ACTION
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: StockManagerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        StockRemoveButton(coordinator, entry.entry_id),
        StockAddButton(coordinator, entry.entry_id),
    ])


class _StockButton(CoordinatorEntity, ButtonEntity):
    _action: str  # "add" or "remove"

    def __init__(self, coordinator: StockManagerCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"stock_manager_{self._action}_{entry_id}"

    async def async_press(self) -> None:
        pid = self.coordinator.current_product_id
        if pid is None:
            return
        await self.coordinator.async_post(_API_ACTION[self._action], pid, 1)


class StockRemoveButton(_StockButton):
    _action = "remove"
    _attr_name = "在庫消費"
    _attr_icon = "mdi:minus-circle-outline"


class StockAddButton(_StockButton):
    _action = "add"
    _attr_name = "在庫追加"
    _attr_icon = "mdi:plus-circle-outline"
