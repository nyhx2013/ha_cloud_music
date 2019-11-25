class MoreInfoHaCloudMusicKodi extends HTMLElement {
  constructor() {
    super()
  }

  
  render() {

  }

  get stateObj() {
    return this._stateObj
  }

  set stateObj(value) {
    this._stateObj = value
    this.render()
  }
}

customElements.define('more-info-ha_cloud_music-kodi', MoreInfoHaCloudMusicKodi);