tools = [
    {
        "name": "unlock",
        "description": "Unlocks the vehicle doors",
        "input_schema": {
            "type": "object",
        },
    },
    {
        "name": "lock",
        "description": "Locks the vehicle doors",
        "input_schema": {
            "type": "object",
        },
    },
    {
        "name": "open_trunk",
        "description": "Opens the vehicle trunk",
        "input_schema": {
            "type": "",
            "type": "object",
        },
    },
    {
        "name": "close_trunk",
        "description": "Closes the vehicle trunk",
        "input_schema": {
            "type": "",
            "type": "object",
        },
    },
    {
        "name": "open_frunk",
        "description": "Opens the vehicle frunk",
        "input_schema": {
            "type": "",
            "type": "object",
        },
    },
    {
        "name": "set_cabin_climate",
        "description": "Sets the vehicle cabin climate",
        "input_schema": {
            "type": "object",
            "properties": {
                "temperature": {
                    "type": "number",
                    "description": "The desired temperature in Celsius"
                }
            },
            "required": ["temperature"]
        },
    },
    {
        "name": "navigate",
        "description": "Navigate to the given latitude and longitude",
        "input_schema": {
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "number",
                    "description": "The latitude in the coordinate pair"
                },
                "longitude": {
                    "type": "number",
                    "description": "The longitude in the coordinate pair"
                }
            },
            "required": ["latitude", "longitude"]
        }
    }
]