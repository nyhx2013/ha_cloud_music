window.ha_cloud_music = {
    eventQueue: {},
    get hass() {
        return document.querySelector('home-assistant').hass
    },
    get entity_id() {
        return 'media_player.yun_yin_le'
    },
    get entity() {
        try {
            return this.hass.states[this.entity_id]
        } catch {
            return null
        }
    },
    get version() {
        return this.entity.attributes.version
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
    // 媒体服务
    callMediaPlayerService(service_name, service_data = {}) {
        this.hass.callService('media_player', service_name, {
            entity_id: this.entity_id,
            ...service_data
        })
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
    onmessage(type, data) {
        this.eventQueue[type](data)
    },
    addEventListener(type, func) {
        this.eventQueue[type] = func
    },
    async load(name) {
        if (Array.isArray(name)) {
            const arr = name.map(ele => {
                return this.load(ele)
            })
            return Promise.all(arr)
        }
        const tagName = `ha_cloud_music-${name}`
        const result = await import(`./${tagName}.js?ver=${this.version}`)
        return {
            tagName,
            result
        }
    }
};

(() => {
    const timer = setInterval(() => {
        if (!ha_cloud_music.entity) return
        clearInterval(timer)
        // 加载模块
        ha_cloud_music.load('player')
        ha_cloud_music.load('tabs').then(async () => {
            await ha_cloud_music.load(['playlist', 'lovelist', 'search', 'setting', 'voice', 'fmlist', 'version'])
            ha_cloud_music.load('panel')
        })
    }, 2000)
})();

