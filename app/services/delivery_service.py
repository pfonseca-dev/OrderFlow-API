import math
from decimal import ROUND_HALF_UP, Decimal


class DeliveryService:
    EARTH_RADIUS = 6371.0

    def calculate_distance(
        self,
        original_latitude: Decimal,
        original_longitude: Decimal,
        destination_latitude: Decimal,
        destination_longitude: Decimal,
    ) -> Decimal:
        origin_lat = math.radians(float(original_latitude))
        origin_lng = math.radians(float(original_longitude))
        destination_lat = math.radians(float(destination_latitude))
        destination_lng = math.radians(float(destination_longitude))

        latitude_difference = destination_lat - origin_lat
        longitude_difference = destination_lng - origin_lng

        haversine = (
            math.sin(latitude_difference / 2) ** 2
            + math.cos(origin_lat)
            * math.cos(destination_lat)
            * math.sin(longitude_difference / 2) ** 2
        )

        distance = 2 * self.EARTH_RADIUS * math.asin(math.sqrt(haversine))

        return Decimal(str(distance)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def calculate_fee(self, distance_km: Decimal) -> Decimal:
        if distance_km <= Decimal("2.00"):
            return Decimal("5.00")

        if distance_km <= Decimal("5.00"):
            return Decimal("8.00")

        if distance_km <= Decimal("10.00"):
            return Decimal("12.00")

        return Decimal("18.00")
