class HaCloudMusicPanel extends HTMLElement {
    constructor() {
        super()
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

    // 创建界面
    created(hass) {
        /* ***************** 基础代码 ***************** */
        const shadow = this.attachShadow({ mode: 'open' });
        // 创建面板
        const ha_card = document.createElement('div');
        ha_card.className = 'ha_cloud_music-panel'
        ha_card.innerHTML = `
        <div class="loading hide">
            <ha-circular-progress active></ha-circular-progress>
        </div>
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
        <ha_cloud_music-version></ha_cloud_music-version>     
        `
        shadow.appendChild(ha_card)
        // 创建样式
        const style = document.createElement('style')
        style.textContent = `
        .hide{display:none;} 
        .loading{
            text-align: center;
            position: fixed;
            width: 100%;
            height: 100vh;
            left: 0;
            top: 0;
            background: rgba(255,255,255,.5);
            z-index: 1000;
        }
        .loading ha-circular-progress{
            position: relative;
            top:50%;
            transform:translateY(-50%);
        }
        
        `
        shadow.appendChild(style);
        // 保存核心DOM对象
        this.shadow = shadow
        this.$ = this.shadow.querySelector.bind(this.shadow)
        // 创建成功
        this.isCreated = true
        const { $ } = this

        ha_cloud_music.showLoading = () => {
            $('.loading').classList.remove('hide')
        }
        ha_cloud_music.hideLoading = () => {
            setTimeout(() => {
                $('.loading').classList.add('hide')
            }, 500)
        }
    }

    // 更新界面数据
    updated() {
        let { $, _stateObj } = this
        $('ha_cloud_music-playlist').updated(_stateObj)
        $('ha_cloud_music-setting').updated(_stateObj)
        $('ha_cloud_music-version').updated(_stateObj)
    }


}

customElements.define('ha_cloud_music-panel', HaCloudMusicPanel);