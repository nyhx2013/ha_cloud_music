class HaCloudMusicPlaylist extends HTMLElement {

    constructor() {
        super()
        this.created()
    }
    // 创建界面
    created() {
        /* ***************** 基础代码 ***************** */
        const shadow = this.attachShadow({ mode: 'open' });
        // 创建面板
        const ha_card = document.createElement('div');
        ha_card.className = 'ha_cloud_music-playlist'
        ha_card.innerHTML = `
            <div class="music-list-panel">
                <ul>
                </ul>
            </div>
        `
        shadow.appendChild(ha_card)
        // 创建样式
        const style = document.createElement('style')
        style.textContent = `
        .music-list-panel{}
        .music-list-panel ul{margin:0;padding:10px 0;list-style:none;}
        .music-list-panel ul li{padding:10px 0;display:flex;    align-items: center; border-bottom:1px dashed #eee;}
        .music-list-panel ul li span{width:calc(100% - 35px);display:block;word-wrap: break-word; word-break: normal;}
        .music-list-panel ul li ha-icon{cursor:pointer;float:right;}
        .music-list-panel ul li.active{color: var(--primary-color);}
        .music-list-panel ul li:last-child{display:flex;}
        .music-list-panel ul li:last-child button{flex:1;padding:10px 0;margin:2px;border:none;
           cursor: pointer;
           color: white;background-color:var(--primary-color);}
        `
        shadow.appendChild(style);
        // 保存核心DOM对象
        this.shadow = shadow
        this.$ = this.shadow.querySelector.bind(this.shadow)
        // 创建成功
        this.isCreated = true

        /* ***************** 附加代码 ***************** */
        let { $ } = this
    }

    updated(stateObj) {
        let { $ } = this
        let attr = stateObj.attributes
        let entity_id = stateObj.entity_id
        let source_list = attr.source_list
        // 音乐列表
        if (source_list && source_list.length > 0) {
            let ul = $('.music-list-panel ul')
            ul.innerHTML = ''
            let fragment = document.createDocumentFragment();
            attr.source_list.forEach((ele, index) => {
                let li = document.createElement('li')
                if (ele === attr.source) {
                    li.className = 'active'
                    li.innerHTML = `<span>${ele}</span> <ha-icon icon="mdi:music"></ha-icon>`
                } else {
                    let span = document.createElement('span')
                    span.textContent = ele
                    li.appendChild(span)
                    let ironIcon = document.createElement('ha-icon')
                    ironIcon.setAttribute('icon', 'mdi:play-circle-outline')
                    ironIcon.onclick = () => {
                        ha_cloud_music.callService('media_player.select_source', {
                            entity_id,
                            source: ele
                        })
                        ha_cloud_music.toast(`开始播放： ${ele}`)
                    }
                    li.appendChild(ironIcon)
                }
                fragment.appendChild(li)
            })
            // 如果有下一页，则显示播放下一页
            let media_playlist = attr.media_playlist
            let obj = media_playlist[0]['load']
            if (obj) {
                // 获取相关信息
                let { id, type, index, total } = obj
                // 当前所有页数的数据
                let count = index * 50
                // console.log(obj, count)
                let li = document.createElement('li')
                let btn1 = document.createElement('button')
                btn1.innerHTML = '播放上一页'
                btn1.onclick = () => {
                    let playIndex = count - 100 + 1
                    ha_cloud_music.toast(`播放第${playIndex}首音乐`)
                    ha_cloud_music.callService('ha_cloud_music.load', { id, type, index: playIndex })
                }
                let btn2 = document.createElement('button')
                btn2.innerHTML = '播放下一页'
                btn2.onclick = () => {
                    let playIndex = count + 1
                    ha_cloud_music.toast(`播放第${playIndex}首音乐`)
                    ha_cloud_music.callService('ha_cloud_music.load', { id, type, index: playIndex })
                }
                // 如果大于第一页，则显示上一页
                if (index > 1) li.appendChild(btn1)
                if (count < total - 50) li.appendChild(btn2)
                fragment.appendChild(li)
            }
            ul.appendChild(fragment)
        }
    }
}
customElements.define('ha_cloud_music-playlist', HaCloudMusicPlaylist);