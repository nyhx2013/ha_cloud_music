class MoreInfoHaCloudMusicKodi extends HTMLElement {
  constructor() {
      super()
      this.icon = {
          play: 'mdi:play-circle-outline',
          pause: 'mdi:pause-circle-outline',            
          shuffle_disabled: 'mdi:shuffle-disabled', //列表播放
          repeat: 'mdi:repeat', //列表循环
          repeat_once: 'mdi:repeat-once', //单曲循环
          shuffle: 'mdi:shuffle', //随机播放
          volume_high: 'mdi:volume-high',
          volume_off: 'mdi:volume-off',
      }
      const shadow = this.attachShadow({mode: 'open'});
      const div = document.createElement('div', {'class': 'root'});
      div.innerHTML = `
             
             <!-- 音量控制 -->
             <div class="volume">
              <div>
                <iron-icon class="volume-off" icon="mdi:volume-high"></iron-icon>
              </div>
              <div>
                  <ha-paper-slider min="0" max="100" />
              </div>
             </div>
                            
             <!-- 源播放器 -->
             <div class="source">
                <paper-input type="search" id="keyInput" placeholder="请输入要搜索的影片"></paper-input>
             </div>
             
             <!-- 音乐面板 -->
             <div class="music-panel">
               <div class="music-list"></div>
             </div>
             
             <!-- 音乐进度 -->
             <div class="progress">
               <div>00:00</div>
               <div>
                  <ha-paper-slider min="0" max="100" value="50" />
               </div>                 
               <div>00:00</div>
             </div>
             
             <!-- 音乐控制 -->
             <div class="controls">
                 <div>
                  <iron-icon class="play_mode" icon="mdi:repeat" style="display:none;"></iron-icon>
                 </div>
                 <div>
                 <iron-icon class="prev" icon="mdi:skip-previous-outline"></iron-icon>
                 </div>
                 <div>
                 <iron-icon class="action" icon="mdi:play-circle-outline"></iron-icon>
                 </div>
                 <div>
                 <iron-icon class="next" icon="mdi:skip-next-outline"></iron-icon>
                 </div>
                 <div>
                 <iron-icon class="controls-list" icon="mdi:playlist-music-outline" style="display:none;"></iron-icon>
                 </div>
             </div>
             
             <div class="mask"></div>              
               
             <div class="loading">
                 <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="margin: auto;transform: translateY(100%); display: block;" width="200px" height="200px" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid">
                  <circle cx="28" cy="75" r="11" fill="#85a2b6">
                    <animate attributeName="fill-opacity" repeatCount="indefinite" dur="1s" values="0;1;1" keyTimes="0;0.2;1" begin="0s"></animate>
                  </circle>

                  <path d="M28 47A28 28 0 0 1 56 75" fill="none" stroke="#bbcedd" stroke-width="10">
                    <animate attributeName="stroke-opacity" repeatCount="indefinite" dur="1s" values="0;1;1" keyTimes="0;0.2;1" begin="0.1s"></animate>
                  </path>
                  <path d="M28 25A50 50 0 0 1 78 75" fill="none" stroke="#dce4eb" stroke-width="10">
                    <animate attributeName="stroke-opacity" repeatCount="indefinite" dur="1s" values="0;1;1" keyTimes="0;0.2;1" begin="0.2s"></animate>
                  </path>
                  </svg>
             </div>
             <div class="toast">
              弹窗提示
             </div>
          
      `
      shadow.appendChild(div);
      // 绑定事件
      const _this = this
      div.querySelector('.action').onclick = function(){
          let icon = this.getAttribute('icon')
          if(icon === _this.icon.play){                
              this.setAttribute('icon', _this.icon.pause)
              // 调用播放服务
              _this.call({entity_id: _this.stateObj.entity_id}, 'media_play')
              _this.toast("播放音乐")
          }else{
              this.setAttribute('icon', _this.icon.play)
              // 调用暂停服务
              _this.call({entity_id: _this.stateObj.entity_id}, 'media_pause')
              _this.toast("暂停音乐")
          }
      }
      div.querySelector('.prev').onclick = function(){
          // 上一曲
          _this.call({entity_id: _this.stateObj.entity_id}, 'media_previous_track')
          _this.toast("播放上一首")
      }
      div.querySelector('.next').onclick = function(){
          // 下一曲
          _this.call({entity_id: _this.stateObj.entity_id}, 'media_next_track')
          _this.toast("播放下一首")
      }
      // 搜索影片
      div.querySelector('#keyInput').onkeydown = function(e){
          if(e.keyCode === 13){
            let value = this.value.trim()
            if(value){
                _this.search(value)
            }
          }
      }
      // 静音
      div.querySelector('.volume-off').onclick = function(){
          let icon = this.getAttribute('icon')
          let is_volume_muted = false
          if(this.icon === _this.icon.volume_high){                                
              this.setAttribute('icon', _this.icon.volume_off)                
              _this.toast("静音")
              is_volume_muted = true
          }else{
              this.setAttribute('icon', _this.icon.volume_high)
              _this.toast("启用音量")
              is_volume_muted = false
          }
          _this.call({
              entity_id: _this.stateObj.entity_id,
              is_volume_muted: is_volume_muted
          }, 'volume_mute')            
      }
      // 调整音量
      div.querySelector('.volume ha-paper-slider').onchange = function(){
          let volume_level = this.value / 100
          _this.call({
              entity_id: _this.stateObj.entity_id,
              volume_level: volume_level
          }, 'volume_set')
          _this.toast(`调整音量到${this.value}`)
      }   
      // 调整进度
      div.querySelector('.progress ha-paper-slider').onchange = function(){
          let attr = _this.stateObj.attributes
          let seek_position = this.value / 100 * attr.media_duration
          
          _this.call({
              entity_id: _this.stateObj.entity_id,
              seek_position: seek_position
          }, 'media_seek')
          
          _this.toast(`调整音乐进度到${seek_position}秒`)
      }
      // 设置样式
      const style = document.createElement('style');
      style.textContent = `
       
       .loading{
          width: 100%;height: 100vh;position: fixed;background: rgba(0,0,0,.7);top: 0;left: 0;display:none;
          z-index:1000;
       }
       .toast{background-color:black;
          color:white;
          text-align:center;
          width:100%;
          position:fixed;
          top:0;left:0;
          z-index:1001;
          display:none;
          opacity: 0;
          padding:22px 10px;
          font-weight:bold;
          font-size:14px;
          transition: opacity 0.5s;}
       
       .source ha-paper-dropdown-menu{width:100%;}
       
       .volume{display:flex;align-items: center;}
       .volume div:nth-child(1){width:40px;text-align:center;cursor:pointer;}
       .volume div:nth-child(2){width:100%;}
       .volume ha-paper-slider{width:100%;}
       
       .progress{display:flex;align-items: center;}
       .progress div{width:40px;}
       .progress div:nth-child(2){width:100%;}
       .progress ha-paper-slider{width:100%;}
          
       .controls{display:flex;text-align:center;align-items: center;}
       .controls div{width:100%;}
       .controls div:nth-child(3) iron-icon{width:40px;height:40px;}
       
       .music-panel{background-size:cover; overflow:auto;}
       .music-panel .music-list{width:100%;height:100%;overflow:auto;}
       .music-list p{padding:5px 10px;margin:0;border-bottom:1px solid silver;font-size:12px;}
       .music-list ul{margin:0;padding:10px 0;list-style:none;font-size:14px;}
        .music-list ul li{padding:10px;display:flex;    align-items: center;}
        .music-list ul li span{width:100%;display:block;}
        .music-list ul li iron-icon{width:30px;}
       
       @media (min-width: 451px){
          .music-panel{height:300px;}       
       }
       @media (max-width: 450px){
          .mask{width: 100%;height: 100vh;position: fixed;background: rgba(0,0,0,.5);top: 0;left: 0;display:none;}
          .music-panel{
              height:calc(100vh - 400px);
          }
       }
      `;
      shadow.appendChild(style);   
      this.shadow = shadow
        
    // 初始化加载本地列表
    if(this.kodi_video_list.length > 0){
      this.loadVideoList(this.kodi_video_list)
    }
  }
  
  showMask(){
      this.shadow.querySelector('.mask').style.display = 'block'
  }
  
  hideMask(){
      this.shadow.querySelector('.mask').style.display = 'none'
  }
  
  showLoading(){
      this.loadingTime = Date.now()
      this.shadow.querySelector('.loading').style.display = 'block'
  }
  
  hideLoading(){
      if(Date.now() - this.loadingTime < 1000){
          setTimeout(()=>{
              this.shadow.querySelector('.loading').style.display = 'none'        
          },1000)
      }else{
          this.shadow.querySelector('.loading').style.display = 'none'
      }
  }
  
  // 提示
  toast(msg){
      let toast = this.shadow.querySelector('.toast')
      if(toast.timer != null){
          clearTimeout(toast.timer)
      }
      toast.innerHTML = msg
      toast.style.display = 'block'
      toast.style.opacity = '1'
      toast.timer = setTimeout(()=>{
          toast.style.opacity = '0'            
          toast.timer = setTimeout(()=>{
              toast.style.display = 'none'
              toast.timer = null
          },500)
      },3000)
  }
  
  // 加载视频列表
  loadVideoList(list){
    let music_list = this.shadow.querySelector('.music-list')
    music_list.innerHTML = ''
    let fragment = document.createDocumentFragment();
    list.forEach((ele, index) => {
        // 添加标题
        let p = document.createElement('p')
        p.textContent = ele.name
        fragment.appendChild(p)
        // 添加播放列表         
        let ul = document.createElement('ul')
        
        let eps = ele.source.eps
        eps.forEach( s => {
            let li = document.createElement('li')
            let span = document.createElement('span')
            span.textContent = s.name
            li.appendChild(span)
            let ironIcon = document.createElement('iron-icon')
            ironIcon.setAttribute('icon','mdi:play-circle-outline')
            ironIcon.onclick = () => {
                // 这里播放音乐
                // console.log(index,ele)                        
                // 德鲁娜酒店
                this.call({
                    entity_id: this.stateObj.entity_id,
                    media_content_id: s.url,
                    media_content_type: 'video'
                },'play_media')                        
                this.toast(`开始播放： ${s.name}`)
            }
            li.appendChild(ironIcon)
            
            ul.appendChild(li)
        })                
        fragment.appendChild(ul)
    })            
    music_list.appendChild(fragment)
  }
  
  get kodi_video_list(){
      try{
        let list = JSON.parse(localStorage['HA-CLOUDE-MUSIC-KODI-VIDEO-LIST'])    
        return Array.isArray(list) ? list : []
      }catch{
        return []
      }
  }
  
  set kodi_video_list(value){
      localStorage['HA-CLOUDE-MUSIC-KODI-VIDEO-LIST'] = JSON.stringify(value)
  }
  
  search(keywords){
    this.showLoading()
    fetch(`https://api.jiluxinqing.com/api/service/vipvideo/video?url=${keywords}`).then(res=>res.json()).then(res=>{
        let { code, data, msg } = res
        if (code === 0) {
            let list = data.data            
            this.loadVideoList(list)
            if(list.length > 0){
                this.kodi_video_list = list
            }
        }else{
            this.toast(msg)
        }
    }).finally(() => {
        this.hideLoading()
    })
  }
  
  // 调用接口
  call(data, service, domain = 'media_player'){
      this.showLoading()
      // 开始执行加载中。。。
      let auth = this.hass.auth
      if(auth.expired){
          auth.refreshAccessToken()
      }
      // 发送查询请求
      fetch(`/api/services/${domain}/${service}`,{
          method:'post',
          body:JSON.stringify(data),
          headers: {
            'Authorization': `${auth.data.token_type} ${auth.accessToken}`
          }
      }).then(res=>res.json()).then(res=>{
        // console.log(res)
      }).finally(()=>{
          //加载结束。。。
          this.hideLoading()
      })
  }
  
  timeForamt(num){
      if(num < 10) return '0'+String(num)
      return String(num)
  }
  
  // 自定义初始化方法
  render(){
      const _this = this
      let attr = this.stateObj.attributes
      let state = this.stateObj.state
      // console.log(this.stateObj)
      this.shadow.querySelector('.controls .action').setAttribute('icon', state==='playing' ? this.icon.pause : this.icon.play)        
      this.shadow.querySelector('.volume .volume-off').setAttribute('icon', attr.is_volume_muted ? this.icon.volume_off : this.icon.volume_high)
      this.shadow.querySelector('.volume ha-paper-slider').value = attr.volume_level * 100
      if('media_position' in attr && 'media_duration' in attr){
        this.shadow.querySelector('.progress div:nth-child(1)').textContent = `${this.timeForamt(Math.floor(attr.media_position/60))}:${this.timeForamt(attr.media_position%60)}`
        this.shadow.querySelector('.progress div:nth-child(3)').textContent = `${this.timeForamt(Math.floor(attr.media_duration/60))}:${this.timeForamt(attr.media_duration%60)}`
        if(attr.media_position <=  attr.media_duration){
            this.shadow.querySelector('.progress ha-paper-slider').value = attr.media_position / attr.media_duration * 100    
        }   
      }
  }    
  
  /* --------------------生命周期回调函数-------------------------------- */
  
  // 当 custom element首次被插入文档DOM时，被调用。
  connectedCallback(){
      
  }
  
  // 当 custom element从文档DOM中删除时，被调用。
  disconnectedCallback(){
      // console.log('当 custom element从文档DOM中删除时，被调用。')
  }
  
  // 当 custom element被移动到新的文档时，被调用。
  adoptedCallback(){
      console.log('当 custom element被移动到新的文档时，被调用。')
  }
     
  get stateObj(){
      return this._stateObj
  }
  
  set stateObj(value){
      this._stateObj = value
      this.render()
  }
}

customElements.define('more-info-ha_cloud_music-kodi', MoreInfoHaCloudMusicKodi);