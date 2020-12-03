window.ha_cloud_music = {
    eventQueue: {},
    get hass() {
        return document.querySelector('home-assistant').hass
    },
    get version() {
        return this.hass.states['media_player.yun_yin_le'].attributes.version
    },
    fetchApi(params) {
        return this.hass.fetchWithAuth('/ha_cloud_music-api', {
            method: 'POST',
            body: JSON.stringify(params)
        }).then(res => res.json())
    },
    callService(service_name, service_data = {}) {
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
    },
    onmessage({ type, data }) {
        this.eventQueue[type](data)
    },
    addEventListener(type, func) {
        this.eventQueue[type] = func
    },
    load(name) {
        return import(`./ha_cloud_music-${name}.js?ver=${this.version}`)
    }
}
// 加载模块
ha_cloud_music.load('player')
ha_cloud_music.load('tabs').then(async () => {
    await ha_cloud_music.load('playlist')
    await ha_cloud_music.load('lovelist')
    await ha_cloud_music.load('search')
    await ha_cloud_music.load('setting')
    await ha_cloud_music.load('voice')
    await ha_cloud_music.load('fmlist')
    ha_cloud_music.load('panel')
})