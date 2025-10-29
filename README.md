# Zmanim MCP Server

[![PyPI version](https://badge.fury.io/py/zmanim-mcp-server.svg)](https://pypi.org/project/zmanim-mcp-server/)

A comprehensive MCP server for calculating Jewish prayer times (zmanim).

## Installation

### Via PyPI (Recommended)
```bash
# For use with Claude Desktop or other MCP clients
uvx zmanim-mcp-server
```

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "zmanim": {
      "command": "uvx",
      "args": ["zmanim-mcp-server"]
    }
  }
}
```

A comprehensive Model Context Protocol (MCP) server for calculating Jewish prayer times (zmanim) using the python-zmanim library.

## Overview

This MCP server provides tools to calculate various Jewish prayer times and astronomical times for any location worldwide. It uses the python-zmanim library, which is a Python port of the KosherJava project, implementing accurate astronomical calculations based on the NOAA algorithm.

## Features

### Available Tools

1. **zmanim_get_sunrise_sunset** - Get sunrise and sunset times
2. **zmanim_get_shema_times** - Get latest times for reciting the morning Shema (GR"A and MG"A opinions)
3. **zmanim_get_tefila_times** - Get latest times for morning prayer/Shacharis (GR"A and MG"A opinions)
4. **zmanim_get_mincha_times** - Get times for afternoon prayer including Mincha Gedola, Mincha Ketana, and Plag HaMincha
5. **zmanim_get_shabbat_times** - Get Shabbat candle lighting and Havdalah times
6. **zmanim_get_daily_times** - Get a comprehensive set of all daily zmanim

### Key Features

- ✅ Support for multiple halachic opinions (GR"A, MG"A)
- ✅ Accurate NOAA-based astronomical calculations
- ✅ Support for any global location with latitude/longitude
- ✅ Timezone-aware calculations
- ✅ Optional date specification (defaults to today)
- ✅ Multiple output formats (Markdown and JSON)
- ✅ Customizable candle lighting offset
- ✅ Comprehensive error handling

## Installation

### Prerequisites

```bash
# Install required Python packages
pip install mcp zmanim --break-system-packages
```

### Setup

1. Save the `zmanim_mcp.py` file to your desired location

2. Configure your MCP client (e.g., Claude Desktop) to use this server:

**For Claude Desktop**, add to your configuration file:

macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "zmanim": {
      "command": "python",
      "args": ["/path/to/zmanim_mcp.py"]
    }
  }
}
```

3. Restart your MCP client

## Usage Examples

### Get Sunrise and Sunset

```
Get sunrise and sunset times for New York City today:
- Location: New York, NY
- Latitude: 40.7128
- Longitude: -74.0060
- Time Zone: America/New_York
```

### Get Latest Shema Times

```
What time is the latest I can say Shema in Jerusalem?
- Location: Jerusalem
- Latitude: 31.7683
- Longitude: 35.2137
- Time Zone: Asia/Jerusalem
```

### Get Shabbat Times

```
Get Shabbat candle lighting and Havdalah times for Chicago this Friday:
- Location: Chicago, IL
- Latitude: 41.8781
- Longitude: -87.6298
- Time Zone: America/Chicago
- Candle lighting offset: 18 minutes (can be customized)
```

### Get Complete Daily Schedule

```
Give me all the prayer times for London today:
- Location: London
- Latitude: 51.5074
- Longitude: -0.1278
- Time Zone: Europe/London
```

## Zmanim Explained

### Morning Times

- **Alos HaShachar (Dawn)**: First light, 72 minutes before sunrise
- **Sunrise (Hanetz HaChama)**: When the sun rises above the horizon
- **Sof Zman Krias Shema**: Latest time to recite the morning Shema
  - **GR"A**: 3 hours after sunrise
  - **MG"A**: 3 temporal hours from dawn (typically earlier)
- **Sof Zman Tefila**: Latest time for morning prayer (Shacharis)
  - **GR"A**: 4 hours after sunrise
  - **MG"A**: 4 temporal hours from dawn (typically earlier)

### Afternoon Times

- **Chatzos**: Solar noon, midpoint between sunrise and sunset
- **Mincha Gedola**: Earliest time for afternoon prayer (30 minutes after midday)
- **Mincha Ketana**: Preferred earliest time for Mincha (2.5 hours before sunset)
- **Plag HaMincha**: 1.25 hours before sunset (latest time according to some opinions)

### Evening Times

- **Sunset (Shkiah)**: When the sun sets below the horizon
- **Tzeis HaKochavim**: Nightfall, when stars appear (72 minutes after sunset)

### Shabbat & Holidays

- **Candle Lighting**: Typically 18-40 minutes before sunset (varies by community)
- **Havdalah**: When Shabbat ends, typically at Tzeis (72 minutes after sunset)

## Halachic Opinions

The server supports calculations according to different halachic authorities:

- **GR"A (Vilna Gaon)**: Calculates day from sunrise to sunset
- **MG"A (Magen Avraham)**: Calculates day from dawn (72 minutes before sunrise) to nightfall

## Response Formats

### Markdown Format (default)
Human-readable format with clear headers and organized sections, perfect for display.

### JSON Format
Machine-readable structured data including ISO 8601 timestamps, suitable for programmatic use.

## Input Parameters

All tools accept the following parameters:

- **location** (required): Name of the location (e.g., "New York, NY")
- **latitude** (required): Latitude in decimal degrees (-90 to 90)
- **longitude** (required): Longitude in decimal degrees (-180 to 180)
- **time_zone** (required): IANA timezone identifier (e.g., "America/New_York")
- **date** (optional): Date in YYYY-MM-DD format (defaults to today)
- **response_format** (optional): "markdown" or "json" (defaults to markdown)

For Shabbat times, there's an additional parameter:
- **candle_lighting_offset** (optional): Minutes before sunset (1-60, default 18)

## Technical Details

### Calculations
- Uses the NOAA (National Oceanic and Atmospheric Administration) algorithm
- Accounts for atmospheric refraction
- Timezone-aware using IANA timezone database
- Elevation can be incorporated in calculations

### Dependencies
- **mcp**: Model Context Protocol SDK
- **zmanim**: Python port of KosherJava zmanim library
- **pydantic**: Input validation and data modeling

## Common Location Examples

| Location | Latitude | Longitude | Timezone |
|----------|----------|-----------|----------|
| Jerusalem | 31.7683 | 35.2137 | Asia/Jerusalem |
| New York | 40.7128 | -74.0060 | America/New_York |
| Los Angeles | 34.0522 | -118.2437 | America/Los_Angeles |
| London | 51.5074 | -0.1278 | Europe/London |
| Paris | 48.8566 | 2.3522 | Europe/Paris |
| Sydney | -33.8688 | 151.2093 | Australia/Sydney |
| Toronto | 43.6532 | -79.3832 | America/Toronto |
| Miami | 25.7617 | -80.1918 | America/New_York |

## Troubleshooting

### Server not appearing in MCP client
1. Check that the path in your configuration is correct
2. Ensure Python and all dependencies are installed
3. Verify the configuration file syntax is valid JSON
4. Restart your MCP client after configuration changes

### Times showing as "N/A"
This typically occurs for locations near the poles where the sun doesn't rise or set on certain days. The calculations handle this gracefully by returning "N/A".

### Timezone errors
Ensure you're using valid IANA timezone identifiers. You can find a list at: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

## License

This MCP server uses the python-zmanim library, which is licensed under the GNU Lesser General Public License v2 or later (LGPLv2+), ported from the KosherJava project.

## Credits

- Based on the [python-zmanim](https://github.com/pinnymz/python-zmanim) library by pinnymz
- Original Java library: [KosherJava](https://github.com/KosherJava/zmanim) by Eliyahu Hershfeld
- NOAA astronomical calculations

## Support

For issues related to:
- **This MCP server**: Please open an issue with details about your configuration and the problem
- **Zmanim calculations**: Refer to the [python-zmanim repository](https://github.com/pinnymz/python-zmanim)
- **Halachic questions**: Consult your local rabbi or posek

## Future Enhancements

Potential additions to consider:
- Hebrew date calculations
- Fast day times
- Molad calculations
- Holiday determination
- Custom opinion configurations
- Multi-day range queries
- Export to calendar formats (iCal)

---

**Note**: This server is for informational purposes. For practical halachic decisions, please consult a qualified rabbi.
