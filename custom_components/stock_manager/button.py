from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import StockManagerCoordinator
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: StockManagerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        StockUseButton(coordinator, entry.entry_id),
        StockAddButton(coordinator, entry.entry_id),
    ])


class _StockButton(CoordinatorEntity, ButtonEntity):
    _action: str  # "add" or "use"

    def __init__(self, coordinator: StockManagerCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"stock_manager_{self._action}_{entry_id}"
        self.entity_id = f"button.stock_manager_{self._action}"

    async def async_press(self) -> None:
        pid = self.coordinator.current_product_id
        if pid is None:
            return
        await self.coordinator.async_post(self._action, pid, 1)


class StockUseButton(_StockButton):
    _action = "use"
    _attr_name = "在庫消費"
    _attr_icon = "mdi:minus-circle-outline"


class StockAddButton(_StockButton):
    _action = "add"
    _attr_name = "在庫追加"
    _attr_icon = "mdi:plus-circle-outline"
