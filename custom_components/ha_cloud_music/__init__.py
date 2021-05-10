async def async_setup_entry(hass, config_entry):
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, "media_player"))
    return True