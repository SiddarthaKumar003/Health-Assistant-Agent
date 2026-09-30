import os
import httpx

from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

PLACES_URL = "https://places.googleapis.com/v1/places:searchNearby"


@tool
def find_nearby_doctors(
    latitude: float,
    longitude: float,
    radius_meters: int = 5000,
    specialty: str = "doctor",
) -> str:
    """
    Find nearby healthcare providers using the user's approximate
    latitude and longitude.

    Use this when the user asks for nearby doctors, clinics,
    hospitals, or healthcare providers.
    """

    if not GOOGLE_MAPS_API_KEY:
        return (
            "Doctor finder is not configured. "
            "GOOGLE_MAPS_API_KEY is missing."
        )

    radius_meters = max(500, min(radius_meters, 50000))

    # Google Places types supported for healthcare searches.
    if specialty.lower() == "hospital":
        included_types = ["hospital"]
    elif specialty.lower() == "clinic":
        included_types = ["medical_clinic"]
    else:
        included_types = ["doctor"]

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": (
            "places.id,"
            "places.displayName,"
            "places.formattedAddress,"
            "places.location,"
            "places.primaryType,"
            "places.googleMapsUri,"
            "places.nationalPhoneNumber,"
            "places.currentOpeningHours,"
            "places.rating,"
            "places.userRatingCount"
        ),
    }

    payload = {
        "includedTypes": included_types,
        "maxResultCount": 10,
        "rankPreference": "DISTANCE",
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude,
                },
                "radius": float(radius_meters),
            }
        },
    }

    try:
        response = httpx.post(
            PLACES_URL,
            headers=headers,
            json=payload,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()
        places = data.get("places", [])

        if not places:
            return (
                "I couldn't find healthcare providers matching "
                "that search near the provided location."
            )

        results = []

        for index, place in enumerate(places, start=1):
            name = place.get(
                "displayName",
                {}
            ).get("text", "Unknown provider")

            address = place.get(
                "formattedAddress",
                "Address unavailable",
            )

            phone = place.get(
                "nationalPhoneNumber",
                "Phone unavailable",
            )

            rating = place.get("rating")
            reviews = place.get("userRatingCount")

            maps_url = place.get(
                "googleMapsUri",
                "",
            )

            opening_hours = place.get(
                "currentOpeningHours",
                {}
            )

            open_now = opening_hours.get(
                "openNow"
            )

            result = (
                f"{index}. {name}\n"
                f"Address: {address}\n"
                f"Phone: {phone}\n"
            )

            if rating is not None:
                result += f"Rating: {rating}"

                if reviews is not None:
                    result += f" ({reviews} reviews)"

                result += "\n"

            if open_now is not None:
                result += (
                    f"Open now: "
                    f"{'Yes' if open_now else 'No'}\n"
                )

            if maps_url:
                result += f"Google Maps: {maps_url}\n"

            results.append(result)

        return (
            "Nearby healthcare providers found. "
            "These are directory/search results and should "
            "not be interpreted as medical recommendations.\n\n"
            + "\n".join(results)
        )

    except httpx.HTTPStatusError as exc:
        return (
            "The nearby healthcare search failed because the "
            f"Maps service returned HTTP {exc.response.status_code}."
        )

    except httpx.RequestError:
        return (
            "I couldn't connect to the nearby healthcare "
            "search service right now."
        )

    except Exception:
        return (
            "An unexpected error occurred while searching "
            "for nearby healthcare providers."
        )