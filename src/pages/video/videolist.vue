<template>
  <!--歌单详情-->
  <div class="details">
    <mm-loading v-model="mmLoadShow" />
    <video ref="video" controls v-if="isPlay" style="width:100%;"></video>
    <music-list :list="list" @select="selectItem"></music-list>
  </div>
</template>

<script>
import { mapActions } from "vuex";
import { getFmList } from "api";
import MmLoading from "base/mm-loading/mm-loading";
import MusicList from "components/music-list/music-list";
import { formatTopSongs } from "assets/js/song";
import { loadMixin } from "assets/js/mixin";

export default {
  name: "detail",
  mixins: [loadMixin],
  components: {
    MmLoading,
    MusicList
  },
  data() {
    return {
      list: [], // 列表
      id: "",
      page: 1,
      size: 12,
      isPlay: false,
      hls: null
    };
  },
  mounted() {
    let { name, album,  type, source } = this.$route.params

    if (!source) {
      this.$router.replace('/music/video')
      return
    }

    let arr = []
    source.forEach((ele, index) => {
      arr.push({
        type,
        album,
        image: 'http://p4.music.126.net/3DCZrxJ4svHIobxLcg_KyQ==/109951164240032297.jpg?param=180y180',
        id: index,
        name: ele.name,
        media_type: 'video',
        singer: name,
        clv_url: ele.url
      })
    })
    this.list = arr
    this._hideLoad();
  },
  beforeRouteLeave (to, from, next){
    this.hls && this.hls.destroy()
    next()
  },
  methods: {
    // 播放暂停事件
    selectItem(item, index) {
      if (item.type === 'movie') {
        if (Hls.isSupported()) {
          if (top.confirm('是否在本地播放')) {
            this.isPlay = true
            let video = this.$refs['video']
            let hls = new Hls();
            hls.loadSource(item.clv_url);
            hls.attachMedia(video);
            hls.on(Hls.Events.MANIFEST_PARSED, function () {
              video.play();
            });
            this.hls = hls
            return
          }
        }
      }
      this.selectPlay({
        list: this.list,
        index
      });
    },
    ...mapActions(["selectPlay"])
  }
};
</script>

<style lang="less" scoped>
.details {
  position: relative;
  width: 100%;
  height: 100%;
  .musicList {
    width: 100%;
    height: 100%;
    .list-btn {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 50px;
      span {
        padding: 5px 20px;
        cursor: pointer;
        user-select: none;
        &:hover {
          color: @text_color_active;
        }
      }
    }
  }
}
</style>
