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
        if (Array.isArray(name)) {
            const arr = name.map(ele => {
                return this.load(ele)
            })
            return Promise.all(arr)
        }
        return import(`./ha_cloud_music-${name}.js?ver=${this.version}`)
    }
}

setTimeout(() => {
    // 加载模块
    ha_cloud_music.load('player')
    ha_cloud_music.load('tabs').then(async () => {
        await ha_cloud_music.load(['playlist', 'lovelist', 'search', 'setting', 'voice', 'fmlist', 'version'])
        ha_cloud_music.load('panel')
    })
}, 1000)
