class HaCloudMusicSearch extends HTMLElement {

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
        ha_card.className = 'ha_cloud_music-search'
        ha_card.innerHTML = `
            <div class="search-box">
                <select class="select">
                    <option value="playlist">网易云歌单</option>
                    <option value="djradio">网易云电台</option>
                    <option value="ximalaya">喜马拉雅专辑</option>
                </select>
                <input type="search" class="input border" />
            </div>
            <div class="search-list">

                <div class="shadow border-sm search-item" style="margin-bottom: 1rem;">
                    <div class="card-body">
                        <p>没啥好说的。。。</p>
                    </div>
                </div>

            </div>
        `
        shadow.appendChild(ha_card)
        // 创建样式
        const style = document.createElement('style')
        style.textContent = `
                *{outline:0}button{cursor:pointer}.btn{padding:3px 21px;line-height:38px;border:0;text-align:center;transition:.3s ease;transition-property:box-shadow,transform;font-size:13.3333px;box-shadow:12px 12px 16px 0 #d4d4d4,-8px -8px 16px #fff}.btn-sm{padding:1px 12px;line-height:30px}.btn-full{width:100%}.btn:hover{box-shadow:4px 4px 7px 0 #d4d4d4,-4px -4px 10px #fff}.btn-cleary:hover{box-shadow:12px 12px 16px 0 #d4d4d4,-8px -8px 16px #fff}.btn:focus{box-shadow:0 0 0 rgba(0,0,0,.2),0 0 0 rgba(255,255,255,.8),inset -8px -8px 20px rgb(255 255 255 / .31),inset 5px 5px 8px #2c2c2c38}.btn:disabled{cursor:no-drop}.btn-link{display:inline-block;text-decoration:none}.btn-default{background:linear-gradient(145deg,#fff,#e6e6e6);color:#000}.btn-default:hover{background:linear-gradient(145deg,#fff,#dadada)}.btn-default:disabled{box-shadow:inset 1px 1px 5px 1px #ccc;background:linear-gradient(145deg,#fff,#fff);color:#aaa}.btn-default:focus{background:linear-gradient(145deg,#fff,#dadada)}.btn-primary{background:linear-gradient(145deg,#4ec8ff,#42a8db);color:#fff}.btn-primary:hover{background:linear-gradient(145deg,#61bfef,#509fc7)}.btn-primary:disabled{box-shadow:inset 1px 1px 5px 1px #ccc;background:linear-gradient(145deg,#fff,#fff);color:#aaa}.btn-primary:focus{background:linear-gradient(145deg,#61bfef,#509fc7)}.btn-secondary{background:linear-gradient(145deg,#b6babd,#999d9f);color:#fff}.btn-secondary:hover{background:linear-gradient(145deg,#a6aaac,#8c8f91)}.btn-secondary:disabled{box-shadow:inset 1px 1px 5px 1px #ccc;background:linear-gradient(145deg,#fff,#fff);color:#aaa}.btn-secondary:focus{background:linear-gradient(145deg,#a6aaac,#8c8f91)}.btn-success{background:linear-gradient(145deg,#a9ec8c,#8ec776);color:#fff}.btn-success:hover{background:linear-gradient(145deg,#a1da88,#87b872)}.btn-success:disabled{box-shadow:inset 1px 1px 5px 1px #ccc;background:linear-gradient(145deg,#fff,#fff);color:#aaa}.btn-success:focus{background:linear-gradient(145deg,#a1da88,#87b872)}.btn-warning{background:linear-gradient(145deg,#e6dc71,#c2b95f);color:#fff}.btn-warning:hover{background:linear-gradient(145deg,#dad16d,#b8b05c)}.btn-warning:disabled{box-shadow:inset 1px 1px 5px 1px #ccc;background:linear-gradient(145deg,#fff,#fff);color:#aaa}.btn-warning:focus{background:linear-gradient(145deg,#dad16d,#b8b05c)}.btn-danger{background:linear-gradient(145deg,#b33964,#963054);color:#fff}.btn-danger:hover{background:linear-gradient(145deg,#ad4368,#923957)}.btn-danger:disabled{box-shadow:inset 1px 1px 5px 1px #ccc;background:linear-gradient(145deg,#fff,#fff);color:#aaa}.btn-danger:focus{background:linear-gradient(145deg,#ad4368,#923957)}.card-body{padding:15px}.card-top{overflow:hidden;text-overflow:ellipsis}.card-top-p{text-align:center;padding:4% 4% 0 4%}.card-title{margin:0;color:#668a9a}.card-body p{margin:0;color:#668a9a91}.card-body a{text-decoration:none}.shadow{box-shadow:-6px -5px 10px white,0px 4px 15px rgba(0,0,0,0.15)}.shadow-sm{box-shadow:1px 1px 2px #cdcbcb,-1px -1px 2px #fff}.shadow-concave{box-shadow:inset 8px 8px 16px #d4d4d4,inset -8px -8px 16px #fff}.border{border-radius:20px}.border-t{border-radius:35px 35px 0 0}.border-b{border-radius:0 0 35px 35px}.border-sm{border-radius:10px}.border-sm-t{border-radius:10px 10px 0 0}.border-sm-b{border-radius:0 0 10px 10px}.border-lg{border-radius:50px}.border-lg-t{border-radius:50px 50px 0 0}.border-lg-b{border-radius:0 0 50px 50px}.border-all{border-radius:50%}hr{margin-bottom:20px}.divider{height:2px;box-shadow:1px 1px 2px #cdcbcb,-1px -1px 2px #fff;border:0}.divider-sm{width:100px;margin-inline-start:unset}.img{max-width:100%}.input{color:#868a9a;text-shadow:1px 1px 0 #fff;padding:16px;background-color:#ffffff00;font-size:16px;width:100%;border:0;outline:0;box-sizing:border-box;box-shadow:inset 2px 2px 6px #babecc,inset -4px -5px 8px #fff;transition:all .2s ease-in-out}.input:hover{box-shadow:inset 2px 2px 2px #babecc,inset -1px -2px 5px #fff}.textarea{color:#868a9a;text-shadow:1px 1px 0 #fff;padding:16px;background-color:#ffffff00;font-size:16px;width:100%;border:0;outline:0;box-sizing:border-box;box-shadow:inset 2px 2px 6px #babecc,inset -4px -5px 8px #fff;transition:all .2s ease-in-out}.textarea:hover{box-shadow:inset 2px 2px 2px #babecc,inset -1px -2px 5px #fff}.fieldset{border:0;margin:0;padding:0;max-width:100%}.legend{width:100%;font-size:1.4rem;margin-bottom:1rem;color:#0000008a}.select{width:100%;border:0;border-radius:20px;padding:15px;box-shadow:-6px -5px 12px white,0px 4px 15px rgba(0,0,0,0.15);background-color:#ffffff00;color:#868a9a}.select:not([multiple]):not([size]){-webkit-appearance:none;-moz-appearance:none;padding-right:20px;background-image:url(data:image/svg+xml;charset=UTF-8,%3Csvg%20width%3D%2224%22%20height%3D%2216%22%20viewBox%3D%220%200%2024%2016%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%0A%20%20%20%20%3Cpolygon%20fill%3D%22%23666%22%20points%3D%2212%201%209%206%2015%206%22%20%2F%3E%0A%20%20%20%20%3Cpolygon%20fill%3D%22%23666%22%20points%3D%2212%2013%209%208%2015%208%22%20%2F%3E%0A%3C%2Fsvg%3E%0A);background-repeat:no-repeat;background-position:99.5% 50%}.radio{border-radius:50%}.radio,.checkbox{display:inline-block;height:25px;width:25px;overflow:hidden;margin-top:-4px;vertical-align:middle;-webkit-appearance:none;-moz-appearance:none;transition:.2s ease-in-out;transition-property:box-shadow;box-shadow:-6px -5px 12px white,0px 4px 15px rgba(0,0,0,0.15);cursor:pointer}
.radio:checked,.checkbox:checked{box-shadow:0 0 0 rgba(0,0,0,.2),0 0 0 rgba(255,255,255,.8),inset 3px 3px 5px #dadada,inset -3px -3px 5px #fff}.radio:disabled,.checkbox:disabled{background-color:#00000024;cursor:no-drop}.radio-label,.checkbox-label{color:#0000008a}.range{box-sizing:border-box;margin:0;vertical-align:middle;max-width:100%;width:100%;-webkit-appearance:none;background:transparent;box-shadow:inset 2px 2px 6px #babecc,inset -4px -5px 8px #fff;padding:3px;border-radius:20px}.range::-webkit-slider-thumb{-webkit-appearance:none;border-radius:50%;cursor:default;top:0;height:20px;width:20px;background:linear-gradient(145deg,#fff,#d8d8d8);box-shadow:2px 2px 3px #dadada,-2px -2px 3px #fff;cursor:pointer}.progress{width:100%}.progress-back{height:24px;border-radius:10px;box-shadow:inset 7px 7px 15px rgba(56,56,56,0.15),inset -7px -7px 20px rgba(255,255,255,1),0px 0 4px rgba(255,255,255,.2)!important}.progress-line{height:16px;background:linear-gradient(145deg,#2995f3,#227dcc);margin-top:-20px;margin-left:4px;border-radius:8px;opacity:1;animation:sliding 3s ease infinite}.n-h1,.n-h2,.n-h3,.n-h4,.n-h5,.n-h6{color:#0000008a;word-break:break-word}
         .ha_cloud_music-search{background-color: #ebecf0;  padding:20px 10px;}
        .search-box {display:flex;}
        .search-box .select{width:150px;margin-right: 10px;}
        .search-item{margin-top:20px;margin-bottom: 1rem;}
        .search-item .shadow-concave{padding: 20px;margin: 10px 0; color: #668a9a;}
        `
        shadow.appendChild(style);
        // 保存核心DOM对象
        this.shadow = shadow
        this.$ = this.shadow.querySelector.bind(this.shadow)
        // 创建成功
        this.isCreated = true

        /* ***************** 附加代码 ***************** */
        let { $ } = this
        let txtSearchInput = $('.search-box .input')
        txtSearchInput.onkeypress = (event) => {
            if (event.keyCode == 13) {
                let value = txtSearchInput.value.trim()
                if (value) {
                    txtSearchInput.value = ''
                    let type = $('.search-box .select').value
                    ha_cloud_music.toast(`正在搜索【${value}】`)
                    ha_cloud_music.fetchApi({
                        type: `search-${type}`,
                        name: value
                    }).then(res => {
                        let fragment = document.createDocumentFragment()
                        res.forEach(ele => {
                            let div = document.createElement('div')
                            div.className = "shadow border-sm search-item"
                            div.innerHTML = `
                            <div class="card-body">
                                <div class="card-top-p">
                                    <img class=" border-sm shadow-sm img" src="${ele.cover}" alt="demo">
                                </div>
                                <p>
                                <hr class="divider">
                                <b>${ele.name}</b> — ${ele.creator}
                                <div class="shadow-concave border-sm">
                                    ${ele.intro}
                                </div>
                                </p>
                                <div style="text-align: right;">
                                    <a class="btn btn-link btn-default border" style="margin-top: 1rem;" 
                                    data-name="${ele.name}"
                                    data-id="${ele.id}">播放</a>
                                </div>
                            </div>
                            `
                            fragment.appendChild(div)
                        })
                        $('.search-list').innerHTML = ''
                        $('.search-list').appendChild(fragment)
                        $('.search-list').onclick = (event) => {
                            let element = event.path[0]
                            let id = element.dataset['id']
                            if (id) {
                                ha_cloud_music.callService('ha_cloud_music.load', { id, type, index: 1 })
                                ha_cloud_music.toast(`开始播放【${element.dataset['name']}】`)
                            }
                        }
                    }).catch(ex => {
                        ha_cloud_music.toast("没有查到数据哦！")
                    })
                }
            }
        }
    }
}
customElements.define('ha_cloud_music-search', HaCloudMusicSearch);