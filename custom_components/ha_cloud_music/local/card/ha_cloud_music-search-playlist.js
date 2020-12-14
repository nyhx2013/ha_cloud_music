class HaCloudMusicSearchPlayList extends HTMLElement {

    // 创建界面
    created(type, value) {
        this.type = type
        /* ***************** 基础代码 ***************** */
        const shadow = this.attachShadow({ mode: 'open' });
        // 创建面板
        const ha_card = document.createElement('div');
        ha_card.className = 'ha-cloud-music-fm-list'
        ha_card.innerHTML = `
        <!-- 电台列表 -->
        <div class="fm-list">
        </div>                
        <!-- 电台信息 -->
        <div class="fm-info hide">
            <div class="info-title"><span>返回</span> <b>音乐台</b></div>
            <ol></ol>
            <button>加载更多</button>
        </div>
        `
        shadow.appendChild(ha_card)
        // 创建样式
        const style = document.createElement('style')
        style.textContent = `
            .ha-cloud-music-fm-list{}
             .fm-list{ text-align: center;
                display: grid; 
                grid-column-gap: 2%;
                grid-row-gap: 8px;
                grid-template-columns: repeat(3, 32%);
            }
            .fm-list img{width:100%;}
            .fm-item,
            .fm-info .info-title span{cursor:pointer;}
            .hide{display:none!important;}
            .fm-info .info-title{padding:10px; border-bottom:1px solid #eee;position: sticky; top:-20px;background-color:white;}
            .fm-info .info-title b{float:right;}
            .fm-info ol li{padding:10px; border-bottom:1px solid #eee;cursor:pointer;}
            .fm-info button{width: 100%; border: none; padding: 10px; color: #03a9f4;}
        `
        shadow.appendChild(style);
        // 保存核心DOM对象
        this.shadow = shadow
        this.$ = this.shadow.querySelector.bind(this.shadow)
        // 创建成功
        this.isCreated = true


        /* ***************** 附加代码 ***************** */
        let { $ } = this
        ha_cloud_music.showLoading()
        // 请求数据
        ha_cloud_music.fetchApi({
            type: `search-${type}`,
            name: value
        }).then(res => {
            const df = document.createDocumentFragment()
            res.forEach(({ id, name, cover }) => {
                const title = name
                const div = document.createElement('div')
                div.classList.add('fm-item')
                div.onclick = () => {
                    // 显示电台信息列表
                    $('.info-title b').textContent = title
                    const button = $('.fm-info button')
                    button.dataset['id'] = id
                    button.dataset['page'] = 1
                    button.classList.remove('hide')
                    this.loadMoreData()
                }
                div.title = title
                div.innerHTML = `<img src="${cover}?param=300y300" /><br/>${title}`
                df.appendChild(div)
            })
            $('.fm-list').appendChild(df)
        }).finally(() => {
            ha_cloud_music.hideLoading()
        })
        // 返回
        $('.info-title span').onclick = () => {
            $('.fm-info').classList.add('hide')
            $('.fm-list').classList.remove('hide')
        }
        // 加载更多
        $('.fm-info button').onclick = () => {
            this.loadMoreData(true)
        }
    }

    loadMoreData() {
        let { $ } = this
        ha_cloud_music.showLoading()
        const button = $('.fm-info button')
        let id = button.dataset['id']
        let page = button.dataset['page']
        let pagesize = 50
        if (page == 1) {
            this.music_list = []
            $('.fm-info ol').innerHTML = ''
            $('.fm-info ol').onclick = (event) => {
                const li = event.path[0]
                const list = this.music_list
                const index = parseInt(li.dataset['index'])
                ha_cloud_music.toast(`开始播放【${list[index].name}】`)
                // 播放FM
                ha_cloud_music.showLoading()
                ha_cloud_music.fetchApi({ type: 'play_media', list, index }).finally(() => {
                    ha_cloud_music.hideLoading()
                })
            }
        }
        ha_cloud_music.fetchApi({
            type: `search-${this.type}`,
            id,
            page,
            size: pagesize
        }).then(res => {
            $('.fm-list').classList.add('hide')
            $('.fm-info').classList.remove('hide')
            const ol = document.createDocumentFragment()
            res.list.forEach(ele => {
                const li = document.createElement('li')
                li.dataset['index'] = this.music_list.length
                li.innerHTML = `${ele.song} - ${ele.singer}`
                ol.appendChild(li)
                this.music_list.push(ele)
            })
            $('.fm-info ol').appendChild(ol)
            button.dataset['page'] = ++page
            // 判断是否能加载更多
            let len = $('.fm-info ol').querySelectorAll('li').length
            if (!res.total || res.total == len) {
                button.classList.add('hide')
            }
        }).finally(() => {
            ha_cloud_music.hideLoading()
        })
    }
}

// 定义DOM对象元素
customElements.define('ha_cloud_music-search-playlist', HaCloudMusicSearchPlayList);