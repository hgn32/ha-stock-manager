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
    known: set[str] = set()

    def _add_new() -> None:
        new = []
        for p in coordinator.data["products"]:
            pid = p["id"]
            if pid not in known:
                known.add(pid)
                new.append(StockUseButton(coordinator, pid))
                new.append(StockAddButton(coordinator, pid))
        if new:
            async_add_entities(new)

    _add_new()
    entry.async_on_unload(coordinator.async_add_listener(_add_new))


class _StockButton(CoordinatorEntity, ButtonEntity):
    _action: str

    def __init__(self, coordinator: StockManagerCoordinator, product_id: str) -> None:
        super().__init__(coordinator)
        self._product_id = product_id
        self._attr_unique_id = f"stock_manager_{self._action}_{product_id}"

    def _product(self) -> dict | None:
        for p in self.coordinator.data["products"]:
            if p["id"] == self._product_id:
                return p
        return None

    @property
    def name(self) -> str:
        p = self._product()
        product_name = p["name"] if p else self._product_id
        label = "消費" if self._action == "use" else "追加"
        return f"{product_name} {label}"

    @property
    def extra_state_attributes(self) -> dict:
        return {"product_id": self._product_id}

    async def async_press(self) -> None:
        await self.coordinator.async_post(self._action, self._product_id, 1)


class StockUseButton(_StockButton):
    _action = "use"
    _attr_icon = "mdi:minus-circle-outline"


class StockAddButton(_StockButton):
    _action = "add"
    _attr_icon = "mdi:plus-circle-outline"
