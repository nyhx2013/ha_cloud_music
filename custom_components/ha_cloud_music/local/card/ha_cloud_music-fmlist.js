class HaCloudMusicFMList extends HTMLElement {

    constructor() {
        super()
        this.created()
    }

    async _fetch(url) {
        try {
            if (url == 'https://rapi.qingting.fm/categories?type=channel' && localStorage["ha_cloud_music-fmlist"]) {
                return JSON.parse(localStorage["ha_cloud_music-fmlist"])
            }
        } catch {

        }
        const res = await fetch(url).then(res => res.json())
        return res.Data
    }

    // 创建界面
    created() {
        /* ***************** 基础代码 ***************** */
        const shadow = this.attachShadow({ mode: 'open' });
        // 创建面板
        const ha_card = document.createElement('div');
        ha_card.className = 'ha-cloud-music-fm-list'
        ha_card.innerHTML = `
        <!-- 电台列表 -->
        <div class="fm-list">
            <!--
            <div class="fm-item">
                <img src="https://p2.music.126.net/WEIm9ckMQ9AmN7kKDn30VQ==/109951163686912767.jpg?param=300y300" />
                <br/>
                音乐台
            </div>
            -->
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
            .ha-cloud-music-fm-list{margin-top:10px;}
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

        // 请求数据
        this._fetch('https://rapi.qingting.fm/categories?type=channel').then(res => {
            // console.log(res)
            if (!localStorage["ha_cloud_music-fmlist"]) {
                localStorage["ha_cloud_music-fmlist"] = JSON.stringify(res)
            }
            const df = document.createDocumentFragment()
            res.forEach(({ id, title }) => {
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
                div.innerHTML = `<img src="https://p2.music.126.net/WEIm9ckMQ9AmN7kKDn30VQ==/109951163686912767.jpg?param=300y300" /><br/>${title}`
                df.appendChild(div)
            })
            $('.fm-list').appendChild(df)
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
                const path = event.composedPath()
                const li = path[0]
                const list = this.music_list
                const index = parseInt(li.dataset['index'])
                ha_cloud_music.toast(`开始播放【${list[index].name}】`)
                // 播放FM
                ha_cloud_music.fetchApi({ type: 'play_media', list, index })
            }
        }
        this._fetch(`https://rapi.qingting.fm/categories/${id}/channels?with_total=true&page=${page}&pagesize=${pagesize}`).then(res => {
            // console.log(res)
            $('.fm-list').classList.add('hide')
            $('.fm-info').classList.remove('hide')
            const ol = document.createDocumentFragment()
            res.items.forEach(ele => {
                const name = (ele.nowplaying && ele.nowplaying.title) || ele.title
                const li = document.createElement('li')
                li.dataset['index'] = this.music_list.length
                li.innerHTML = `${name} - ${ele.title}`
                ol.appendChild(li)
                this.music_list.push({
                    album: ele.categories[0].title,
                    duration: ele.audience_count,
                    id: ele.content_id,
                    image: ele.cover,
                    name,
                    song: name,
                    singer: ele.title,
                    type: 'url',
                    url: `http://lhttp.qingting.fm/live/${ele.content_id}/64k.mp3`
                })
            })
            $('.fm-info ol').appendChild(ol)
            button.dataset['page'] = ++page
            // 判断是否能加载更多
            let len = $('.fm-info ol').querySelectorAll('li').length
            if (res.total == len) {
                button.classList.add('hide')
            }
        }).finally(() => {
            ha_cloud_music.hideLoading()
        })
    }
}

// 定义DOM对象元素
customElements.define('ha_cloud_music-fmlist', HaCloudMusicFMList);