window.ha_cloud_music = {
    get hass() {
        return document.querySelector('home-assistant').hass
    },
    fetchApi(params) {
        return this.hass.fetchWithAuth('/ha_cloud_music-api', {
            method: 'POST',
            body: JSON.stringify(params)
        }).then(res => res.json())
    },
    callService(service_name, service_data = {}){
        let arr = service_name.split('.')
        let domain = arr[0]
        let service = arr[1]
        this.hass.callService(domain, service, service_data)
    },
    fire(type, data) {
        const event = new Event(type, {
            bubbles: true,
            cancelable: false,
            composed: true
        });
        event.detail = data;
        document.querySelector('home-assistant').dispatchEvent(event);
    },
    toast(message) {
        this.fire("hass-notification", { message })
    }
}

import('./ha_cloud_music-player.js')
import('./ha_cloud_music-tabs.js').then(async () => {
    await import('./ha_cloud_music-playlist.js')
    await import('./ha_cloud_music-search.js')
    await import('./ha_cloud_music-setting.js')
    await import('./ha_cloud_music-voice.js')
    await import('./ha_cloud_music-fmlist.js')
    import('./ha_cloud_music-panel.js')
})