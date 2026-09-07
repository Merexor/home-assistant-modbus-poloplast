"""Top-level device class that groups the individual subsystems."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from modbus_connection import ModbusError

from .subsystems.controller import Controller
from .subsystems.energy import Energy
from .subsystems.sensors import Sensors

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit


@dataclass
class UpdateReport:
    """Detailed result of a polling update."""

    updated: list[str] = field(default_factory=list)
    failed: dict[str, ModbusError] = field(default_factory=dict)


class Poloplast:
    """A Poloplast ventilation controller reached through a ModbusUnit."""

    def __init__(self, unit: ModbusUnit) -> None:
        """Initialize the device object with subsystems."""
        self._unit = unit

        # Instantiate our component representations
        self.controller = Controller(unit)
        self.sensors = Sensors(unit)
        self.energy = Energy(unit)

        # Polling schedules groups
        self._readings = ("sensors", "energy")
        self._settings = ("controller",)

    async def async_update_readings(self) -> UpdateReport:
        """Update environmental metrics and energy registers."""
        report = UpdateReport()
        await self._async_poll(self._readings, report)
        return report

    async def async_update_settings(self) -> UpdateReport:
        """Update control registers."""
        report = UpdateReport()
        await self._async_poll(self._settings, report)
        return report

    async def async_update(self) -> UpdateReport:
        """Update all data groups in one pass."""
        report = UpdateReport()
        await self._async_poll(self._settings, report)
        await self._async_poll(self._readings, report)
        return report

    async def _async_poll(self, categories: tuple[str, ...], report: UpdateReport) -> None:
        """Execute async reads on the target subsystems."""
        for name in categories:
            try:
                # Update but bypass internal notifications to avoid duplicate triggers
                await getattr(self, name).async_update(notify=False)
            except ModbusError as err:
                report.failed[name] = err
            else:
                report.updated.append(name)

        # Bulk-notify listeners of successful updates
        for name in report.updated:
            getattr(self, name).notify()

    async def async_read_raw(self) -> dict[str, dict[int, int | bool]]:
        """Read all physical values undecoded for developer diagnostics."""
        raw: dict[str, dict[int, int | bool]] = {}
        for name in ("controller", "sensors", "energy"):
            comp_raw = await getattr(self, name).async_read_raw(notify=False)
            for space, mapping in comp_raw.items():
                raw.setdefault(space, {}).update(mapping)
        return raw
