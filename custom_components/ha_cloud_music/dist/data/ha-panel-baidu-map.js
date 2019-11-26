class HaPanelBaiduMap extends HTMLElement {
  constructor() {
      super()
      const shadow = this.attachShadow({mode: 'open'});
      const div = document.createElement('div', {'class': 'root'});
      div.innerHTML = `
          <app-toolbar>
          </app-toolbar>
          <div id="baidu-map"></dvi>
      `
      
      shadow.appendChild(div)
       // 设置样式
      const style = document.createElement('style');
      style.textContent = `
          app-header, app-toolbar {
              background-color: var(--primary-color);
              font-weight: 400;
              color: var(--text-primary-color, white);
          }
          #baidu-map{width:100%;height:calc(100vh - 64px); z-index: 0;}
      `;
      shadow.appendChild(style); 
      this.shadow = shadow
  }
  
  ready(){
      if(window.BMap){
          console.log(window.BMap)
          console.log('%O',this)
            // 添加标题
            let toolbar = this.shadow.querySelector('app-toolbar')
            if(toolbar.children.length === 0){
                  console.log('%O',toolbar)              
                    let menuButton = document.createElement('ha-menu-button')
                    menuButton.hass = this.hass
                    menuButton.narrow = true
                    toolbar.appendChild(menuButton)
                    
                    let title = document.createElement('div')
                    title.setAttribute('main-title','')
                    title.textContent = '百度地图'
                    toolbar.appendChild(title)
                    
                    var mp = new BMap.Map(this.shadow.querySelector('#baidu-map'));
                    mp.centerAndZoom(new BMap.Point(116.3964, 39.9093), 10);
                    mp.enableScrollWheelZoom();                      
                    var canvasLayer = new BMap.CanvasLayer({
                      update: update
                    });

                    function update() {
                      var ctx = this.canvas.getContext("2d");

                      if (!ctx) {
                        return;
                      }

                      ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

                      var temp = {};
                      ctx.fillStyle = "rgba(50, 50, 255, 0.7)";
                      ctx.beginPath();
                      var data = [
                        new BMap.Point(116.297047, 39.979542),
                        new BMap.Point(116.321768, 39.88748),
                        new BMap.Point(116.494243, 39.956539)
                      ];

                      for (var i = 0, len = data.length; i < len; i++) {
                        var pixel = mp.pointToPixel(data[i]);
                        ctx.fillRect(pixel.x, pixel.y, 30, 30);
                      }
                    }
                    mp.addOverlay(canvasLayer);
            }              
      }        
  }
  
  loadScript(src){
      return new Promise((resolve, reject) => {
        let id = btoa(src)
        let ele = document.getElementById(id)
        if(ele){
          resolve()
          return
        }
        let script = document.createElement('script')
        script.id = id
        script.src = src
        script.onload = function () {
          resolve()
        }
        document.querySelector('head').appendChild(script)
      })
  }
  
  get panel(){
     return this._panel 
  }
  
  set panel(value){
      this._panel = value
      this.loadScript(`https://api.map.baidu.com/getscript?v=3.0&ak=${value.config.ak}`).then(res=>{
          this.ready()
      })
  }
}

customElements.define('ha-panel-baidu-map', HaPanelBaiduMap);