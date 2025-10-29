from typing import Any, Optional
import datetime
from enum import Enum
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict
import zmanim
from zmanim.zmanim_calendar import ZmanimCalendar
from zmanim.util.geo_location import GeoLocation


# Initialize FastMCP server
mcp = FastMCP("zmanim_mcp")


class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"


# ============================================================================
# Helper Functions
# ============================================================================

def create_calendar(location: str, latitude: float, longitude: float, 
                   time_zone: str, date: Optional[datetime.date] = None,
                   candle_lighting_offset: int = 18) -> ZmanimCalendar:
    """
    Create a ZmanimCalendar instance with the given location parameters.
    
    Args:
        location: Name of the location
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        time_zone: IANA timezone identifier (e.g., 'America/New_York')
        date: Optional date for calculations (defaults to today)
        candle_lighting_offset: Minutes before sunset for candle lighting (default 18)
        
    Returns:
        Configured ZmanimCalendar instance
    """
    geo_location = GeoLocation(
        name=location,
        latitude=latitude,
        longitude=longitude,
        time_zone=time_zone,
    )
    
    calendar = ZmanimCalendar(
        candle_lighting_offset=candle_lighting_offset,
        geo_location=geo_location,
        date=date
    )
    
    return calendar


def format_time(dt: Optional[datetime.datetime]) -> str:
    """
    Format a datetime object to a readable time string.
    
    Args:
        dt: Datetime object to format
        
    Returns:
        Formatted time string in "HH:MM AM/PM" format, or "N/A" if datetime is None
    """
    if dt is None:
        return "N/A"
    return dt.strftime("%I:%M %p")


def format_time_with_date(dt: Optional[datetime.datetime]) -> str:
    """
    Format a datetime object to include date and time.
    
    Args:
        dt: Datetime object to format
        
    Returns:
        Formatted string in "YYYY-MM-DD HH:MM AM/PM" format, or "N/A" if datetime is None
    """
    if dt is None:
        return "N/A"
    return dt.strftime("%Y-%m-%d %I:%M %p")


# ============================================================================
# Input Models
# ============================================================================

class LocationInput(BaseModel):
    """Base input model for location-based zmanim queries."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    location: str = Field(
        ..., 
        description="Name of the location (e.g., 'Jerusalem', 'New York, NY', 'London')",
        min_length=1,
        max_length=100
    )
    latitude: float = Field(
        ..., 
        description="Latitude coordinate in decimal degrees (e.g., 40.7128 for New York)",
        ge=-90.0,
        le=90.0
    )
    longitude: float = Field(
        ..., 
        description="Longitude coordinate in decimal degrees (e.g., -74.0060 for New York)",
        ge=-180.0,
        le=180.0
    )
    time_zone: str = Field(
        ..., 
        description="IANA timezone identifier (e.g., 'America/New_York', 'Asia/Jerusalem', 'Europe/London')",
        min_length=1
    )
    date: Optional[str] = Field(
        default=None,
        description="Optional date for calculations in YYYY-MM-DD format (defaults to today if not provided)"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable"
    )


class CandleLightingInput(LocationInput):
    """Input model for candle lighting time queries."""
    candle_lighting_offset: int = Field(
        default=18,
        description="Minutes before sunset to light candles (typically 18-40 minutes depending on custom)",
        ge=1,
        le=60
    )


# ============================================================================
# Tool Implementations
# ============================================================================

@mcp.tool(
    name="zmanim_get_sunrise_sunset",
    annotations={
        "title": "Get Sunrise and Sunset Times",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def get_sunrise_sunset(params: LocationInput) -> str:
    """
    Get sunrise and sunset times for a specified location and date.
    
    This tool calculates the times of sunrise and sunset based on astronomical
    calculations, taking into account the geographic location. The calculations
    use the NOAA algorithm for accuracy.
    
    Args:
        params (LocationInput): Input parameters containing:
            - location (str): Name of the location
            - latitude (float): Latitude in decimal degrees (-90 to 90)
            - longitude (float): Longitude in decimal degrees (-180 to 180)
            - time_zone (str): IANA timezone identifier
            - date (Optional[str]): Date in YYYY-MM-DD format (defaults to today)
            - response_format (ResponseFormat): 'markdown' or 'json'
    
    Returns:
        str: Formatted sunrise and sunset times in the requested format
        
    Example:
        For New York on a winter day, sunrise might be at 7:15 AM and sunset at 4:30 PM.
    """
    # Parse date if provided
    date = None
    if params.date:
        date = datetime.datetime.strptime(params.date, "%Y-%m-%d").date()
    
    # Create calendar
    calendar = create_calendar(
        params.location,
        params.latitude,
        params.longitude,
        params.time_zone,
        date
    )
    
    # Get times
    sunrise = calendar.sunrise()
    sunset = calendar.sunset()
    
    if params.response_format == ResponseFormat.JSON:
        import json
        return json.dumps({
            "location": params.location,
            "date": (date or datetime.date.today()).isoformat(),
            "timezone": params.time_zone,
            "sunrise": format_time_with_date(sunrise),
            "sunset": format_time_with_date(sunset),
            "sunrise_iso": sunrise.isoformat() if sunrise else None,
            "sunset_iso": sunset.isoformat() if sunset else None
        }, indent=2)
    
    # Markdown format
    date_str = (date or datetime.date.today()).strftime("%B %d, %Y")
    return f"""# Sunrise and Sunset Times

**Location:** {params.location}  
**Date:** {date_str}  
**Timezone:** {params.time_zone}

- **Sunrise:** {format_time(sunrise)}
- **Sunset:** {format_time(sunset)}
"""


@mcp.tool(
    name="zmanim_get_shema_times",
    annotations={
        "title": "Get Latest Times for Shema",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def get_shema_times(params: LocationInput) -> str:
    """
    Get the latest times for reciting the morning Shema according to different opinions.
    
    This tool calculates the deadline for reciting the morning Shema (Krias Shema)
    according to two major halachic opinions: the GR"A (Vilna Gaon) and the
    Magen Avraham (MG"A). The GR"A calculation is 3 hours after sunrise, while
    the MG"A is based on 3 temporal hours from dawn (72 minutes before sunrise).
    
    Args:
        params (LocationInput): Input parameters containing location and date information
    
    Returns:
        str: Latest times for Shema according to both opinions in the requested format
        
    Note:
        The MG"A time is typically earlier and more stringent than the GR"A time.
    """
    date = None
    if params.date:
        date = datetime.datetime.strptime(params.date, "%Y-%m-%d").date()
    
    calendar = create_calendar(
        params.location,
        params.latitude,
        params.longitude,
        params.time_zone,
        date
    )
    
    # Get times according to different opinions
    shema_gra = calendar.sof_zman_shma_gra()
    shema_mga = calendar.sof_zman_shma_mga()
    
    if params.response_format == ResponseFormat.JSON:
        import json
        return json.dumps({
            "location": params.location,
            "date": (date or datetime.date.today()).isoformat(),
            "timezone": params.time_zone,
            "sof_zman_shema_gra": format_time_with_date(shema_gra),
            "sof_zman_shema_mga": format_time_with_date(shema_mga),
            "sof_zman_shema_gra_iso": shema_gra.isoformat() if shema_gra else None,
            "sof_zman_shema_mga_iso": shema_mga.isoformat() if shema_mga else None
        }, indent=2)
    
    date_str = (date or datetime.date.today()).strftime("%B %d, %Y")
    return f"""# Latest Times for Shema

**Location:** {params.location}  
**Date:** {date_str}  
**Timezone:** {params.time_zone}

## Opinions:

- **GR"A (Vilna Gaon):** {format_time(shema_gra)}
- **MG"A (Magen Avraham):** {format_time(shema_mga)}

*Note: The MG"A time is typically earlier and is the more stringent opinion.*
"""


@mcp.tool(
    name="zmanim_get_tefila_times",
    annotations={
        "title": "Get Latest Times for Morning Prayer",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def get_tefila_times(params: LocationInput) -> str:
    """
    Get the latest times for morning prayer (Tefila/Shacharis) according to different opinions.
    
    This tool calculates the deadline for reciting the morning Shemoneh Esrei according
    to two major halachic opinions: the GR"A (4 hours after sunrise) and the MG"A
    (4 temporal hours from dawn).
    
    Args:
        params (LocationInput): Input parameters containing location and date information
    
    Returns:
        str: Latest times for Tefila according to both opinions in the requested format
    """
    date = None
    if params.date:
        date = datetime.datetime.strptime(params.date, "%Y-%m-%d").date()
    
    calendar = create_calendar(
        params.location,
        params.latitude,
        params.longitude,
        params.time_zone,
        date
    )
    
    tefila_gra = calendar.sof_zman_tfila_gra()
    tefila_mga = calendar.sof_zman_tfila_mga()
    
    if params.response_format == ResponseFormat.JSON:
        import json
        return json.dumps({
            "location": params.location,
            "date": (date or datetime.date.today()).isoformat(),
            "timezone": params.time_zone,
            "sof_zman_tefila_gra": format_time_with_date(tefila_gra),
            "sof_zman_tefila_mga": format_time_with_date(tefila_mga),
            "sof_zman_tefila_gra_iso": tefila_gra.isoformat() if tefila_gra else None,
            "sof_zman_tefila_mga_iso": tefila_mga.isoformat() if tefila_mga else None
        }, indent=2)
    
    date_str = (date or datetime.date.today()).strftime("%B %d, %Y")
    return f"""# Latest Times for Morning Prayer (Tefila)

**Location:** {params.location}  
**Date:** {date_str}  
**Timezone:** {params.time_zone}

## Opinions:

- **GR"A (Vilna Gaon):** {format_time(tefila_gra)}
- **MG"A (Magen Avraham):** {format_time(tefila_mga)}

*Note: The MG"A time is typically earlier.*
"""


@mcp.tool(
    name="zmanim_get_mincha_times",
    annotations={
        "title": "Get Times for Mincha Prayer",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def get_mincha_times(params: LocationInput) -> str:
    """
    Get the times for Mincha (afternoon prayer) including Mincha Gedola and Mincha Ketana.
    
    This tool calculates when the afternoon prayer can be recited:
    - Mincha Gedola: Earliest time (30 minutes after midday/chatzos)
    - Mincha Ketana: Preferred earliest time (2.5 hours before sunset)
    - Plag HaMincha: Latest time according to some opinions (1.25 hours before sunset)
    
    Args:
        params (LocationInput): Input parameters containing location and date information
    
    Returns:
        str: All relevant Mincha times in the requested format
    """
    date = None
    if params.date:
        date = datetime.datetime.strptime(params.date, "%Y-%m-%d").date()
    
    calendar = create_calendar(
        params.location,
        params.latitude,
        params.longitude,
        params.time_zone,
        date
    )
    
    chatzos = calendar.chatzos()
    mincha_gedola = calendar.mincha_gedola()
    mincha_ketana = calendar.mincha_ketana()
    plag_hamincha = calendar.plag_hamincha()
    
    if params.response_format == ResponseFormat.JSON:
        import json
        return json.dumps({
            "location": params.location,
            "date": (date or datetime.date.today()).isoformat(),
            "timezone": params.time_zone,
            "chatzos": format_time_with_date(chatzos),
            "mincha_gedola": format_time_with_date(mincha_gedola),
            "mincha_ketana": format_time_with_date(mincha_ketana),
            "plag_hamincha": format_time_with_date(plag_hamincha),
            "chatzos_iso": chatzos.isoformat() if chatzos else None,
            "mincha_gedola_iso": mincha_gedola.isoformat() if mincha_gedola else None,
            "mincha_ketana_iso": mincha_ketana.isoformat() if mincha_ketana else None,
            "plag_hamincha_iso": plag_hamincha.isoformat() if plag_hamincha else None
        }, indent=2)
    
    date_str = (date or datetime.date.today()).strftime("%B %d, %Y")
    return f"""# Mincha (Afternoon Prayer) Times

**Location:** {params.location}  
**Date:** {date_str}  
**Timezone:** {params.time_zone}

## Times:

- **Chatzos (Midday):** {format_time(chatzos)}
- **Mincha Gedola (Earliest):** {format_time(mincha_gedola)}
- **Mincha Ketana (Preferred):** {format_time(mincha_ketana)}
- **Plag HaMincha:** {format_time(plag_hamincha)}

*Note: Mincha can be prayed from Mincha Gedola until sunset, with Mincha Ketana being the preferred earliest time.*
"""


@mcp.tool(
    name="zmanim_get_shabbat_times",
    annotations={
        "title": "Get Shabbat Candle Lighting and Havdalah Times",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def get_shabbat_times(params: CandleLightingInput) -> str:
    """
    Get Shabbat candle lighting and Havdalah times for a specified location and date.
    
    This tool calculates:
    - Candle lighting time (before sunset, typically 18-40 minutes depending on custom)
    - Sunset time (when Shabbat begins)
    - Tzeis HaKochavim (nightfall, when Shabbat ends, 72 minutes after sunset)
    
    Args:
        params (CandleLightingInput): Input parameters including:
            - location, latitude, longitude, time_zone, date (from LocationInput)
            - candle_lighting_offset: Minutes before sunset (default 18)
    
    Returns:
        str: Shabbat times in the requested format
        
    Note:
        Different communities have different customs for candle lighting time.
        Jerusalem uses 40 minutes, while many communities use 18 minutes.
    """
    date = None
    if params.date:
        date = datetime.datetime.strptime(params.date, "%Y-%m-%d").date()
    
    calendar = create_calendar(
        params.location,
        params.latitude,
        params.longitude,
        params.time_zone,
        date,
        candle_lighting_offset=params.candle_lighting_offset
    )
    
    candle_lighting = calendar.candle_lighting()
    sunset = calendar.sunset()
    tzeis = calendar.tzais_72()  # 72 minutes after sunset for havdalah
    
    if params.response_format == ResponseFormat.JSON:
        import json
        return json.dumps({
            "location": params.location,
            "date": (date or datetime.date.today()).isoformat(),
            "timezone": params.time_zone,
            "candle_lighting_offset_minutes": params.candle_lighting_offset,
            "candle_lighting": format_time_with_date(candle_lighting),
            "sunset": format_time_with_date(sunset),
            "havdalah_tzeis_72": format_time_with_date(tzeis),
            "candle_lighting_iso": candle_lighting.isoformat() if candle_lighting else None,
            "sunset_iso": sunset.isoformat() if sunset else None,
            "havdalah_tzeis_72_iso": tzeis.isoformat() if tzeis else None
        }, indent=2)
    
    date_str = (date or datetime.date.today()).strftime("%B %d, %Y")
    return f"""# Shabbat Times

**Location:** {params.location}  
**Date:** {date_str}  
**Timezone:** {params.time_zone}

## Friday Evening:

- **Candle Lighting:** {format_time(candle_lighting)} ({params.candle_lighting_offset} minutes before sunset)
- **Sunset (Shabbat Begins):** {format_time(sunset)}

## Saturday Evening:

- **Havdalah (Tzeis HaKochavim):** {format_time(tzeis)} (72 minutes after sunset)
- **Shabbat Ends:** {format_time(tzeis)}

*Note: Candle lighting customs vary by community. Jerusalem uses 40 minutes before sunset.*
"""


@mcp.tool(
    name="zmanim_get_daily_times",
    annotations={
        "title": "Get All Daily Zmanim",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def get_daily_times(params: LocationInput) -> str:
    """
    Get a comprehensive set of daily zmanim (Jewish prayer times) for a location.
    
    This tool provides all major zmanim for the day including:
    - Alos HaShachar (dawn)
    - Sunrise
    - Latest times for Shema (GR"A and MG"A)
    - Latest times for Tefila (GR"A and MG"A)
    - Chatzos (midday)
    - Mincha times
    - Sunset
    - Tzeis HaKochavim (nightfall)
    
    Args:
        params (LocationInput): Input parameters containing location and date information
    
    Returns:
        str: Complete set of daily zmanim in the requested format
        
    Example:
        Use this tool to get a complete daily schedule of prayer times for any location.
    """
    date = None
    if params.date:
        date = datetime.datetime.strptime(params.date, "%Y-%m-%d").date()
    
    calendar = create_calendar(
        params.location,
        params.latitude,
        params.longitude,
        params.time_zone,
        date
    )
    
    # Get all times
    alos = calendar.alos_72()
    sunrise = calendar.sunrise()
    shema_gra = calendar.sof_zman_shma_gra()
    shema_mga = calendar.sof_zman_shma_mga()
    tefila_gra = calendar.sof_zman_tfila_gra()
    tefila_mga = calendar.sof_zman_tfila_mga()
    chatzos = calendar.chatzos()
    mincha_gedola = calendar.mincha_gedola()
    mincha_ketana = calendar.mincha_ketana()
    plag_hamincha = calendar.plag_hamincha()
    sunset = calendar.sunset()
    tzeis = calendar.tzais_72()
    
    if params.response_format == ResponseFormat.JSON:
        import json
        return json.dumps({
            "location": params.location,
            "date": (date or datetime.date.today()).isoformat(),
            "timezone": params.time_zone,
            "times": {
                "alos_hashachar_72": format_time_with_date(alos),
                "sunrise": format_time_with_date(sunrise),
                "sof_zman_shema_gra": format_time_with_date(shema_gra),
                "sof_zman_shema_mga": format_time_with_date(shema_mga),
                "sof_zman_tefila_gra": format_time_with_date(tefila_gra),
                "sof_zman_tefila_mga": format_time_with_date(tefila_mga),
                "chatzos": format_time_with_date(chatzos),
                "mincha_gedola": format_time_with_date(mincha_gedola),
                "mincha_ketana": format_time_with_date(mincha_ketana),
                "plag_hamincha": format_time_with_date(plag_hamincha),
                "sunset": format_time_with_date(sunset),
                "tzeis_hakochavim_72": format_time_with_date(tzeis)
            },
            "times_iso": {
                "alos_hashachar_72": alos.isoformat() if alos else None,
                "sunrise": sunrise.isoformat() if sunrise else None,
                "sof_zman_shema_gra": shema_gra.isoformat() if shema_gra else None,
                "sof_zman_shema_mga": shema_mga.isoformat() if shema_mga else None,
                "sof_zman_tefila_gra": tefila_gra.isoformat() if tefila_gra else None,
                "sof_zman_tefila_mga": tefila_mga.isoformat() if tefila_mga else None,
                "chatzos": chatzos.isoformat() if chatzos else None,
                "mincha_gedola": mincha_gedola.isoformat() if mincha_gedola else None,
                "mincha_ketana": mincha_ketana.isoformat() if mincha_ketana else None,
                "plag_hamincha": plag_hamincha.isoformat() if plag_hamincha else None,
                "sunset": sunset.isoformat() if sunset else None,
                "tzeis_hakochavim_72": tzeis.isoformat() if tzeis else None
            }
        }, indent=2)
    
    date_str = (date or datetime.date.today()).strftime("%B %d, %Y")
    return f"""# Daily Zmanim

**Location:** {params.location}  
**Date:** {date_str}  
**Timezone:** {params.time_zone}

## Morning Times:

- **Alos HaShachar (Dawn):** {format_time(alos)} (72 minutes before sunrise)
- **Sunrise:** {format_time(sunrise)}
- **Latest Shema (GR"A):** {format_time(shema_gra)}
- **Latest Shema (MG"A):** {format_time(shema_mga)}
- **Latest Tefila (GR"A):** {format_time(tefila_gra)}
- **Latest Tefila (MG"A):** {format_time(tefila_mga)}

## Afternoon Times:

- **Chatzos (Midday):** {format_time(chatzos)}
- **Mincha Gedola:** {format_time(mincha_gedola)}
- **Mincha Ketana:** {format_time(mincha_ketana)}
- **Plag HaMincha:** {format_time(plag_hamincha)}

## Evening Times:

- **Sunset:** {format_time(sunset)}
- **Tzeis HaKochavim (Nightfall):** {format_time(tzeis)} (72 minutes after sunset)
"""


def main():
    """Entry point for the package."""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()