from datetime import datetime

from database.repositories.snapshot_repository import SnapshotRepository


_cache = {}

_volume_cache = {}


class SnapshotService:

    @staticmethod
    def save_if_changed(
            contract_id,
            contract_code,
            contract_description,
            market_type,
            last_price,
            volume,
            oi,
            snapshot_time
    ):
        current = (
            last_price,
            volume,
            oi
        )

        previous = _cache.get(contract_id)

        if previous == current:
            return False

        previous_volume = _volume_cache.get(
            contract_id,
            0
        )

        volume = volume or 0

        previous_volume = previous_volume or 0

        volume_delta = max(
            volume - previous_volume,
            0
        )

        _volume_cache[contract_id] = volume

        _cache[contract_id] = current

        SnapshotRepository.save(
            contract_id,
            contract_code,
            contract_description,
            market_type,
            last_price,
            volume,
            volume_delta,
            oi,
            snapshot_time
        )

        return True