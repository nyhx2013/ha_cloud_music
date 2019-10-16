<template>
  <!--排行榜-->
  <div class="topList">
    <mm-loading v-model="mmLoadShow" />
    <div class="search-head">
      <input
        class="search-input"
        type="text"
        placeholder="视频名称"
        v-model.trim="searchValue"
        @keyup.enter="onEnter"
      />
      <div style="padding-top:10px;">注意：这是一个测试功能，可以使用DLNA将视频投到电视上观看</div>
    </div>

    <template v-if="!mmLoadShow">
      <div class="topList-head">视频列表</div>
      <div class="topList-content">
        <div class="list-item" v-for="(item,index) in hotList" :key="index" :title="item.name">
          <router-link :to="{name:`music-videolist`,params:item}" tag="div" class="topList-item">
            <img class="cover-img" v-lazy="`${item.picUrl}?param=200y200`" />
            <h3 class="name">{{item.name}}</h3>
          </router-link>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { getVideoList, searchVideoList } from "api";
import MmLoading from "base/mm-loading/mm-loading";
import { loadMixin } from "assets/js/mixin";

export default {
  name: "play-list",
  mixins: [loadMixin],
  components: {
    MmLoading
  },
  data() {
    return {
      searchValue: '',
      list: [], // 云音乐特色榜
      hotList: [] // 热门歌单
    };
  },
  created() {
    Promise.all([getVideoList()]).then(([hotList]) => {
      this.hotList = hotList;
      this._hideLoad();
    });
  },
  methods: {
    onEnter() {
      let { searchValue } = this
      if (searchValue) {
        searchVideoList({ keywords: searchValue }).then(res => {
          this.hotList = res;
        })
      }
    }
  }
};
</script>

<style lang="less" scoped>
@import "~assets/css/mixin";

  .search-head {
    width:100%;
    padding: 10px 15px;
    background: @search_bg_coloe;
    .search-input {
      width:90%;
      height: 40px;
      box-sizing: border-box;
      padding: 0 15px;
      border: 1px solid @btn_color;
      outline: 0;
      background: transparent;
      color: @text_color_active;
      font-size: @font_size_medium;
      box-shadow: 0 0 1px 0 #fff inset;
      &::placeholder {
        color: @text_color;
      }
    }
  }


.topList {
  position: relative;
  width: 100%;
  height: 100%;
  overflow-x: hidden;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  &-head {
    width: 100%;
    height: 34px;
    line-height: 34px;
    padding: 20px 0;
    font-size: @font_size_large;
    color: @text_color_active;
  }
  &-content {
    overflow: hidden;
  }
  .list-item {
    float: left;
    width: calc(~"100% / 7");
    .topList-item {
      width: 130px;
      text-align: center;
      cursor: pointer;
      margin: 0 auto 20px;
      &:hover {
        color: #fff;
      }
      .name {
        height: 30px;
        line-height: 30px;
        font-size: @font_size_medium;
        .no-wrap();
      }
      @media (max-width: 1100px) {
        width: 80%;
      }
    }
    @media (max-width: 1500px) {
      width: calc(~"100% / 6");
    }
    @media (max-width: 1400px), (max-width: 960px) {
      width: calc(~"100% / 5");
    }
    @media (max-width: 1280px), (max-width: 768px) {
      width: calc(~"100% / 4");
    }
    @media (max-width: 540px) {
      width: calc(~"100% / 3");
    }
  }
}
</style>
