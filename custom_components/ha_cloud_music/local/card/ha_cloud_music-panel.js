class HaCloudMusicPanel extends HTMLElement {
    /*
    * 触发事件
    * type: 事件名称
    * data: 事件参数
    */
    fire(type, data) {
        const event = new Event(type, {
            bubbles: true,
            cancelable: false,
            composed: true
        });
        event.detail = data;
        this.dispatchEvent(event);
    }

    /*
     * 调用服务
     * service: 服务名称(例：light.toggle)
     * service_data：服务数据(例：{ entity_id: "light.xiao_mi_deng_pao" } )
     */
    callService(service_name, service_data = {}) {
        let arr = service_name.split('.')
        let domain = arr[0]
        let service = arr[1]
        this._hass.callService(domain, service, service_data)
    }

    // 通知
    toast(message) {
        this.fire("hass-notification", { message })
    }

    /*
     * 接收HA核心对象
     */
    set hass(hass) {
        this._hass = hass
        if (!this.isCreated) {
            this.created(hass)
        }
    }

    get stateObj() {
        return this._stateObj
    }

    // 接收当前状态对象
    set stateObj(value) {
        this._stateObj = value
        // console.log(value)
        if (this.isCreated) this.updated()
    }

    fetchApi(params) {
        return this._hass.fetchWithAuth('/ha_cloud_music-api', {
            method: 'POST',
            body: JSON.stringify(params)
        }).then(res => res.json())
    }

    // 创建界面
    created(hass) {
        /* ***************** 基础代码 ***************** */
        const shadow = this.attachShadow({ mode: 'open' });
        // 创建面板
        const ha_card = document.createElement('div');
        ha_card.className = 'ha_cloud_music-panel'
        ha_card.innerHTML = `
        <ha_cloud_music-tabs>
            <div data-title="列表">
                <ha_cloud_music-playlist></ha_cloud_music-playlist>
            </div>
            <div data-title="设置">
                <ha_cloud_music-setting></ha_cloud_music-setting>
            </div>
            <div data-title="语音">
                <ha_cloud_music-voice></ha_cloud_music-voice>
            </div>
            <div data-title="广播">
                <ha_cloud_music-fmlist></ha_cloud_music-fmlist>
            </div>
            <div data-title="最爱">
                <ha_cloud_music-lovelist></ha_cloud_music-lovelist>               
            </div>
        </ha_cloud_music-tabs>        
        `
        shadow.appendChild(ha_card)
        // 创建样式
        const style = document.createElement('style')
        style.textContent = `
        
        `
        shadow.appendChild(style);
        // 保存核心DOM对象
        this.shadow = shadow
        this.$ = this.shadow.querySelector.bind(this.shadow)
        // 创建成功
        this.isCreated = true
    }

    // 更新界面数据
    updated() {
        let { $, _stateObj } = this
        $('ha_cloud_music-playlist').updated(_stateObj)
        $('ha_cloud_music-setting').updated(_stateObj)
    }


}

customElements.define('ha_cloud_music-panel', HaCloudMusicPanel);